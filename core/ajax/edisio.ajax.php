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

try {
	require_once dirname(__FILE__) . '/../../../../core/php/core.inc.php';
	include_file('core', 'authentification', 'php');

	if (!isConnect('admin')) {
		throw new Exception('401 Unauthorized');
	}

	if (init('action') == 'restartDeamon') {
		config::save('allowStartDeamon', 1, 'edisio');
		$port = config::byKey('port', 'edisio', 'none');
		if ($port == 'none') {
			ajax::success();
		}
		edisio::stopDeamon();
		if (edisio::deamonRunning()) {
			throw new Exception(__('Impossible d\'arrêter le démon', __FILE__));
		}
		log::clear('edisiocmd');
		edisio::runDeamon(init('debug', 0));
		ajax::success();
	}

	if (init('action') == 'stopDeamon') {
		edisio::stopDeamon();
		if (edisio::deamonRunning()) {
			throw new Exception(__('Impossible d\'arrêter le démon', __FILE__));
		}
		config::save('allowStartDeamon', 0, 'edisio');
		ajax::success();
	}

	if (init('action') == 'restartSlaveDeamon') {
		if (config::byKey('jeeNetwork::mode') == 'master') {
			$jeeNetwork = jeeNetwork::byId(init('id'));
			if (!is_object($jeeNetwork)) {
				throw new Exception(__('Impossible de trouver l\'esclave : ', __FILE__) . init('id'));
			}
			$jeeNetwork->sendRawRequest('restartDeamon', array('plugin' => 'edisio', 'debug' => init('debug', 0)));
		}
		ajax::success();
	}

	if (init('action') == 'stopSlaveDeamon') {
		if (config::byKey('jeeNetwork::mode') == 'master') {
			$jeeNetwork = jeeNetwork::byId(init('id'));
			if (!is_object($jeeNetwork)) {
				throw new Exception(__('Impossible de trouver l\'esclave : ', __FILE__) . init('id'));
			}
			$jeeNetwork->sendRawRequest('stopDeamon', array('plugin' => 'edisio'));
		}
		ajax::success();
	}

	throw new Exception('Aucune methode correspondante');
	/*     * *********Catch exeption*************** */
} catch (Exception $e) {
	ajax::error(displayExeption($e), $e->getCode());
}
?>
