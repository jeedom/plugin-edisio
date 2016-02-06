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

require_once dirname(__FILE__) . '/../../../core/php/core.inc.php';

function edisio_update() {
	foreach (eqLogic::byType('edisio') as $eqLogic) {
		$device = edisio::devicesParameters($eqLogic->getConfiguration('device'));
		foreach ($device['commands'] as $command) {
			$cmd = $eqLogic->getCmd(null, $command['logicalId']);
			if (is_object($cmd) && $cmd->getDisplay('generic_type') == '' && isset($command['display']['generic_type'])) {
				$cmd->setDisplay('generic_type', $command['display']['generic_type']);
				$cmd->save();
			}
		}
	}
}

function edisio_remove() {

}

?>
