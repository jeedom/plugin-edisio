<?php

/* This file is part of Jeedom.
 *
 * Jeedom is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Jeedom is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Jeedom. If not, see <http://www.gnu.org/licenses/>.
 */
require_once dirname(__FILE__) . "/../../../../core/php/core.inc.php";

if (!jeedom::apiAccess(init('apikey'), 'edisio')) {
	echo 'Clef API non valide, vous n\'êtes pas autorisé à effectuer cette action';
	die();
}
if (init('test') != '') {
	echo 'OK';
	die();
}
$result = json_decode(file_get_contents("php://input"), true);
if (!is_array($result)) {
	die();
}

if (isset($result['learn_mode'])) {
	if ($result['learn_mode'] == 1) {
		config::save('include_mode', 1, 'edisio');
		event::add('edisio::includeState', array(
			'mode' => 'learn',
			'state' => 1)
		);
	} else {
		config::save('include_mode', 0, 'edisio');
		event::add('edisio::includeState', array(
			'mode' => 'learn',
			'state' => 0)
		);
	}
	die();
}

if (isset($result['devices'])) {
	foreach ($result['devices'] as $key => $datas) {
		$edisio = edisio::byLogicalId($datas['id'], 'edisio');
		if (!is_object($edisio)) {
			$edisio = edisio::createFromDef($datas);
			if (!is_object($edisio)) {
				log::add('edisio', 'debug', 'Aucun équipement trouvé pour : ' . secureXSS($datas['id']));
				die();
			}
			event::add('jeedom::alert', array(
				'level' => 'warning',
				'page' => 'edisio',
				'message' => '',
			));
			event::add('edisio::includeDevice', $edisio->getId());
		}

		if (!$edisio->getIsEnable()) {
			continue;
		}
		if ($datas['mid'] == '01' || $datas['mid'] == '02' || $datas['mid'] == '03' || $datas['mid'] == '04' || $datas['mid'] == '05' || $datas['mid'] == '07' || $datas['mid'] == '09') {
			$logicalId = 'bt' . $datas['bt'];
			$value = $datas['value'];
			$cmdArray = array($logicalId);
			if ($datas['mid'] == '1') {
				$cmdArray = array($logicalId, $logicalId . 'long');
			}
			foreach ($cmdArray as $logicalIdToCheck) {
				$cmd = $edisio->getCmd('info', $logicalIdToCheck);
				if (!is_object($cmd) && config::byKey('autoDiscoverEqLogic', 'edisio') != 0) {
					$cmd = new edisioCmd();
					$config = array(
						'name' => $logicalIdToCheck,
						'type' => 'info',
						'subtype' => 'binary',
						'isVisible' => 1,
						'isHistorized' => 0,
						'unite' => '',
						'eventOnly' => 1,
						'logicalId' => $logicalIdToCheck,
					);
					$cmd->setEqLogic_id($edisio->getId());
					utils::a2o($cmd, $config);
					$cmd->save();
				}
			}
			if (in_array($datas['value'], array("up", "down")) and $datas['mid'] == '01') {
				$cmd = $edisio->getCmd('info', $logicalId . 'long');
			} else {
				$cmd = $edisio->getCmd('info', $logicalId);
			}
			if (is_object($cmd)) {
				if ($value == 'toggle' && $cmd->getSubType() == 'binary') {
					$value = $cmd->execCmd();
					$value = ($value != 0) ? 0 : 1;
				} else if ($value == 'toggle' && $cmd->getSubType() == 'numeric') {
					$value = $cmd->execCmd();
					$value = ($value != 0) ? $cmd->getConfiguration('minValue', 0) : $cmd->getConfiguration('maxValue', 100);
				} else if ($value == 'up' && $cmd->getSubType() == 'binary') {
					$value = 1;
				} else if ($value == 'down' && $cmd->getSubType() == 'binary') {
					$value = 0;
				} else if ($value == 'up' && $cmd->getSubType() == 'numeric') {
					$value = $cmd->execCmd();
					$range = $cmd->getConfiguration('maxValue', 100) - $cmd->getConfiguration('minValue', 0);
					$value += $range / 10;
					if ($value > $cmd->getConfiguration('maxValue', 100)) {
						$value = $cmd->getConfiguration('minValue', 0);
					}
				}
				$cmd->event($value);
				if ($datas['battery'] > 100) {
					$datas['battery'] = 100;
				}
				$edisio->batteryStatus($datas['battery']);
				if (null !== $edisio->getCmd('info', 'battery')) {
					$edisio->getCmd('info', 'battery')->event($datas['battery']);
				}
			}
			continue;
		}

		foreach ($edisio->getCmd('info') as $cmd) {
			$logicalId = $cmd->getLogicalId();
			if (isset($datas[$logicalId])) {
				if ($logicalId == 'battery') {
					if ($datas[$logicalId] > 100) {
						$datas[$logicalId] = 100;
					}
					$cmd->event($datas[$logicalId]);
					$edisio->batteryStatus($datas[$logicalId]);
				} else {
					$cmd->event(trim($datas[$logicalId]));
				}
			}
		}
	}
}