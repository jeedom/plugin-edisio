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

if (!jeedom::apiAccess(init('apikey'))) {
	connection::failed();
	echo 'Clef API non valide, vous n\'êtes pas autorisé à effectuer cette action';
	die();
}

if (isset($_GET['test'])) {
	echo 'OK';
	die();
}

if (!isset($_GET['id'])) {
	die();
}

$edisio = edisio::byLogicalId($_GET['id'], 'edisio');
if (!is_object($edisio)) {
	$edisio = edisio::createFromDef($_GET);
	if (!is_object($edisio)) {
		log::add('edisio', 'debug', 'Aucun équipement trouvé pour : ' . secureXSS($_GET['id']));
		die();
	}
}

if ($_GET['mid'] == 1 || $_GET['mid'] == 2 || $_GET['mid'] == 3 || $_GET['mid'] == 4 || $_GET['mid'] == 5 || $_GET['mid'] == 7 || $_GET['mid'] == 9) {
	$logicalId = 'bt' . $_GET['bt'];
	$value = $_GET['value'];
	$cmdArray = array($logicalId,$logicalId. 'long');
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
	if (in_array($value,array("up", "down"))) {
		$cmd = $edisio->getCmd('info', $logicalId. 'long');
	} else {
		$cmd = $edisio->getCmd('info', $logicalId);
	}
	if (is_object($cmd)) {
		if ($value == 'toggle' && $cmd->getSubType() == 'binary') {
			$value = $cmd->execCmd();
			$value = ($value != 0) ? 0 : 1;
		}
		else if ($value == 'toggle' && $cmd->getSubType() == 'numeric') {
			$value = $cmd->execCmd();
			$value = ($value != 0) ? $cmd->getConfiguration('minValue', 0) : $cmd->getConfiguration('maxValue', 100);
		}
		else if ($value == 'up' && $cmd->getSubType() == 'binary') {
			$value = 1;
		}
		else if ($value == 'down' && $cmd->getSubType() == 'binary') {
			$value = 0;
		}
		else if ($value == 'up' && $cmd->getSubType() == 'numeric') {
			$value = $cmd->execCmd();
			$range = $cmd->getConfiguration('maxValue', 100) - $cmd->getConfiguration('minValue', 0);
			$value += $range / 10;
			if ($value > $cmd->getConfiguration('maxValue', 100)) {
				$value = $cmd->getConfiguration('minValue', 0);
			}
		};
		$cmd->event($value);
	}
}

foreach ($edisio->getCmd('info') as $cmd) {
	$logicalId = $cmd->getLogicalId();
	if (isset($_GET[$logicalId])) {
		if ($logicalId == 'battery') {
			if ($_GET[$logicalId] > 100) {
				$_GET[$logicalId] = 100;
			}
			$cmd->event($_GET[$logicalId]);
			if ($edisio->getIsEnable() == 1 && $edisio->getConfiguration('noBatterieCheck', 0) != 1) {
				$edisio->batteryStatus($_GET[$logicalId]);
			}
		} else {
			$value = trim($_GET[$logicalId]);
			$cmd->event($value);
		}
	}
}