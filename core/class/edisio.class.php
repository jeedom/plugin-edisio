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
/* * ***************************Includes********************************* */
require_once dirname(__FILE__) . '/../../../../core/php/core.inc.php';
class edisio extends eqLogic {
	/*     * *************************Attributs****************************** */
	/*     * ***********************Methode static*************************** */
	public static function cronDaily() {
		foreach (eqLogic::byType('edisio') as $eqLogic) {
			$deviceParameter = edisio::devicesParameters($eqLogic->getConfiguration('device'));
			if (isset($deviceParameter) && isset($deviceParameter['battery_type'])) {
				$eqLogic->setConfiguration('battery_type', $deviceParameter['battery_type']);
				$eqLogic->save();
			}
		}
	}
	public static function createFromDef($_def) {
		event::add('jeedom::alert', array(
			'level' => 'warning',
			'page' => 'edisio',
			'message' => __('Nouveau module detecté', __FILE__),
		));
		sleep(2);
		$banId = explode(' ', config::byKey('banRfxId', 'edisio'));
		if (in_array($_def['id'], $banId)) {
			event::add('jeedom::alert', array(
				'level' => 'danger',
				'page' => 'edisio',
				'message' => __('Le module a un id banni. Inclusion impossible', __FILE__),
			));
			return false;
		}
		if (!isset($_def['mid']) || !isset($_def['id'])) {
			log::add('edisio', 'error', 'Information manquante pour ajouter l\'équipement : ' . print_r($_def, true));
			event::add('jeedom::alert', array(
				'level' => 'danger',
				'page' => 'edisio',
				'message' => __('Information manquante pour ajouter l\'équipement. Inclusion impossible', __FILE__),
			));
			return false;
		}
		$eqLogic = edisio::byLogicalId($_def['id'], 'edisio');
		if (!is_object($eqLogic)) {
			$eqLogic = new edisio();
			$eqLogic->setName($_def['id']);
		}
		$eqLogic->setLogicalId($_def['id']);
		$eqLogic->setEqType_name('edisio');
		$eqLogic->setIsEnable(1);
		$eqLogic->setIsVisible(1);
		$eqLogic->setConfiguration('device', $_def['mid']);
		$model = $eqLogic->getModelList();
		if (count($model) > 0) {
			$eqLogic->setConfiguration('iconModel', array_keys($model)[0]);
		}
		$eqLogic->save();
		$eqLogic->applyModuleConfiguration();
		event::add('jeedom::alert', array(
			'level' => 'warning',
			'page' => 'edisio',
			'message' => __('Module inclu avec succès', __FILE__),
		));
		sleep(2);
		return $eqLogic;
	}

	public static function devicesParameters($_device = '') {
		$return = array();
		foreach (ls(dirname(__FILE__) . '/../config/devices', '*') as $dir) {
			$path = dirname(__FILE__) . '/../config/devices/' . $dir;
			if (!is_dir($path)) {
				continue;
			}
			$files = ls($path, '*.json', false, array('files', 'quiet'));
			foreach ($files as $file) {
				try {
					$content = file_get_contents($path . '/' . $file);
					if (is_json($content)) {
						$return += json_decode($content, true);
					}
				} catch (Exception $e) {

				}
			}
		}
		if (isset($_device) && $_device != '') {
			if (isset($return[$_device])) {
				return $return[$_device];
			}
			return array();
		}
		return $return;
	}

	public static function dependancy_info() {
		$return = array();
		$return['progress_file'] = '/tmp/dependancy_edisio_in_progress';
		if (exec('sudo dpkg --get-selections | grep -E "python\-serial|python\-request|python\-pyudev" | grep -v desinstall | wc -l') >= 3) {
			$return['state'] = 'ok';
		} else {
			$return['state'] = 'nok';
		}
		return $return;
	}
	public static function dependancy_install() {
		log::remove('edisio_update');
		$cmd = 'sudo /bin/bash ' . dirname(__FILE__) . '/../../resources/install.sh';
		$cmd .= ' >> ' . log::getPathToLog('edisio_dependancy') . ' 2>&1 &';
		exec($cmd);
	}

	public static function deamon_info() {
		$return = array();
		$return['log'] = 'edisio';
		$return['state'] = 'nok';
		$pid_file = '/tmp/edisiod.pid';
		if (file_exists($pid_file)) {
			if (posix_getsid(trim(file_get_contents($pid_file)))) {
				$return['state'] = 'ok';
			} else {
				shell_exec('sudo rm -rf ' . $pid_file . ' 2>&1 > /dev/null;rm -rf ' . $pid_file . ' 2>&1 > /dev/null;');
			}
		}
		$return['launchable'] = 'ok';
		$port = config::byKey('port', 'edisio');
		if ($port != 'auto') {
			$port = jeedom::getUsbMapping($port);
			if (@!file_exists($port)) {
				$return['launchable'] = 'nok';
				$return['launchable_message'] = __('Le port n\'est pas configuré', __FILE__);
			}
			exec('sudo chmod 777 ' . $port . ' > /dev/null 2>&1');
		}
		return $return;
	}
	public static function deamon_stop() {
		$pid_file = '/tmp/edisiod.pid';
		if (file_exists($pid_file)) {
			$pid = intval(trim(file_get_contents($pid_file)));
			system::kill($pid);
		}
		system::kill('edisiod.py');
		system::fuserk(config::byKey('socketport', 'edisio'));
		$port = config::byKey('port', 'edisio');
		if ($port != 'auto') {
			system::fuserk(jeedom::getUsbMapping($port));
		}
	}
	public static function deamon_start() {
		self::deamon_stop();
		$deamon_info = self::deamon_info();
		if ($deamon_info['launchable'] != 'ok') {
			throw new Exception(__('Veuillez vérifier la configuration', __FILE__));
		}
		$port = config::byKey('port', 'edisio');
		if ($port != 'auto') {
			$port = jeedom::getUsbMapping($port);
		}
		$edisio_path = realpath(dirname(__FILE__) . '/../../resources/edisiod');
		$cmd = '/usr/bin/python ' . $edisio_path . '/edisiod.py';
		$cmd .= ' --device ' . $port;
		$cmd .= ' --loglevel ' . log::convertLogLevel(log::getLogLevel('edisio'));
		$cmd .= ' --socketport ' . config::byKey('socketport', 'edisio');
		$cmd .= ' --callback ' . network::getNetworkAccess('internal', 'proto:127.0.0.1:port:comp') . '/plugins/edisio/core/php/jeeEdisio.php';
		$cmd .= ' --apikey ' . jeedom::getApiKey('edisio');
		$cmd .= ' --cycle ' . config::byKey('cycle', 'edisio');
		log::add('edisio', 'info', 'Lancement démon edisiod : ' . $cmd);
		exec($cmd . ' >> ' . log::getPathToLog('edisio') . ' 2>&1 &');
		$i = 0;
		while ($i < 30) {
			$deamon_info = self::deamon_info();
			if ($deamon_info['state'] == 'ok') {
				break;
			}
			sleep(1);
			$i++;
		}
		if ($i >= 30) {
			log::add('edisio', 'error', 'Impossible de lancer le démon EDISIO, vérifiez la configuration et le log edisiod', 'unableStartDeamon');
			return false;
		}
		message::removeAll('edisio', 'unableStartDeamon');
		sleep(2);
		self::sendIdToDeamon();
		config::save('include_mode', 0, 'edisio');
		log::add('edisio', 'info', 'Démon EDISIO lancé');
		return true;
	}

	public static function sendIdToDeamon() {
		foreach (self::byType('edisio') as $eqLogic) {
			$eqLogic->allowDevice();
			usleep(300);
		}
	}

	public static function changeIncludeState($_state) {
		$value = json_encode(array('apikey' => jeedom::getApiKey('rfxcom'), 'cmd' => ($_state == 1) ? 'learnin' : 'learnout'));
		$socket = socket_create(AF_INET, SOCK_STREAM, 0);
		socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'edisio'));
		socket_write($socket, $value, strlen($value));
		socket_close($socket);
	}

/*     * *********************Methode d'instance************************* */
	public function getModelList($_conf = '') {
		if ($_conf == '') {
			$_conf = $this->getConfiguration('device');
		}
		$modelList = array();
		$files = array();
		foreach (ls(dirname(__FILE__) . '/../config/devices', '*') as $dir) {
			if (!is_dir(dirname(__FILE__) . '/../config/devices/' . $dir)) {
				continue;
			}
			$files[$dir] = ls(dirname(__FILE__) . '/../config/devices/' . $dir, $_conf . '_*.jpg', false, array('files', 'quiet'));
			if (file_exists(dirname(__FILE__) . '/../config/devices/' . $dir . $_conf . '.jpg')) {
				$selected = 0;
				if ($dir . $_conf == $this->getConfiguration('iconModel')) {
					$selected = 1;
				}
				$modelList[$dir . $_conf] = array(
					'value' => __('Défaut', __FILE__),
					'selected' => $selected,
				);
			}
			if (count($files[$dir]) == 0) {
				unset($files[$dir]);
			}
		}
		$replace = array(
			$_conf => '',
			'.jpg' => '',
			'_' => ' ',
		);
		foreach ($files as $dir => $images) {
			foreach ($images as $imgname) {
				$selected = 0;
				if ($dir . str_replace('.jpg', '', $imgname) == $this->getConfiguration('iconModel')) {
					$selected = 1;
				}
				$modelList[$dir . str_replace('.jpg', '', $imgname)] = array(
					'value' => ucfirst(trim(str_replace(array_keys($replace), $replace, $imgname))),
					'selected' => $selected,
				);
			}
		}
		return $modelList;
	}

	public function preRemove() {
		$this->disallowDevice();
	}

	public function preInsert() {
		if ($this->getLogicalId() == '') {
			for ($i = 0; $i < 20; $i++) {
				$logicalId = strtoupper(str_pad(dechex(mt_rand()), 8, '0', STR_PAD_LEFT));
				$result = eqLogic::byLogicalId($logicalId, 'edisio');
				if (!is_object($result)) {
					$this->setLogicalId($logicalId);
					break;
				}
			}
			$this->allowDevice();
		}
	}

	public function postSave() {
		if ($this->getConfiguration('applyDevice') != $this->getConfiguration('device')) {
			$this->applyModuleConfiguration();
		} else {
			$this->allowDevice();
		}
	}

	public function postUpdate() {
		if ($this->getConfiguration('applyDevice') != $this->getConfiguration('device')) {
			$this->applyModuleConfiguration();
		}
	}

	public function allowDevice() {
		$value = array('apikey' => jeedom::getApiKey('edisio'), 'cmd' => 'add');
		$value['device'] = array(
			'id' => $this->getLogicalId(),
		);
		$value = json_encode($value);
		$socket = socket_create(AF_INET, SOCK_STREAM, 0);
		socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'edisio'));
		socket_write($socket, $value, strlen($value));
		socket_close($socket);
	}

	public function disallowDevice() {
		if ($this->getLogicalId() == '') {
			return;
		}
		$value = json_encode(array('apikey' => jeedom::getApiKey('edisio'), 'cmd' => 'remove', 'device' => array('id' => $this->getLogicalId())));
		$socket = socket_create(AF_INET, SOCK_STREAM, 0);
		socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'edisio'));
		socket_write($socket, $value, strlen($value));
		socket_close($socket);
	}

	public function applyModuleConfiguration() {
		$this->setConfiguration('applyDevice', $this->getConfiguration('device'));
		$this->save();
		if ($this->getConfiguration('device') == '') {
			return true;
		}
		$device = self::devicesParameters($this->getConfiguration('device'));
		if (!is_array($device)) {
			return true;
		}
		if (isset($device['configuration'])) {
			foreach ($device['configuration'] as $key => $value) {
				$this->setConfiguration($key, $value);
			}
		}
		if (isset($device['category'])) {
			foreach ($device['category'] as $key => $value) {
				$this->setCategory($key, $value);
			}
		}
		if (isset($device['battery_type'])) {
			$this->setConfiguration('battery_type', $device['battery_type']);
		}
		$cmd_order = 0;
		$link_cmds = array();
		$link_actions = array();
		$arrayToRemove = [];
		if (isset($device['commands'])) {
			foreach ($this->getCmd() as $eqLogic_cmd) {
				$exists = 0;
				foreach ($device['commands'] as $command) {
					if ($command['logicalId'] == $eqLogic_cmd->getLogicalId()) {
						$exists++;
					}
				}
				if ($exists < 1) {
					$arrayToRemove[] = $eqLogic_cmd;
				}
			}
			foreach ($arrayToRemove as $cmdToRemove) {
				try {
					$cmdToRemove->remove();
				} catch (Exception $e) {

				}
			}
			foreach ($device['commands'] as $command) {
				$cmd = null;
				try {
					if ($cmd == null || !is_object($cmd)) {
						$cmd = new edisioCmd();
						$cmd->setOrder($cmd_order);
						$cmd->setEqLogic_id($this->getId());
					} else {
						$command['name'] = $cmd->getName();
						if (isset($command['display'])) {
							unset($command['display']);
						}
					}
					utils::a2o($cmd, $command);
					$cmd->save();
					if (isset($command['value'])) {
						$link_cmds[$cmd->getId()] = $command['value'];
					}
					if (isset($command['configuration']) && isset($command['configuration']['updateCmdId'])) {
						$link_actions[$cmd->getId()] = $command['configuration']['updateCmdId'];
					}
					$cmd_order++;
				} catch (Exception $exc) {

				}
			}
		}
		if (count($link_cmds) > 0) {
			foreach ($this->getCmd() as $eqLogic_cmd) {
				foreach ($link_cmds as $cmd_id => $link_cmd) {
					if ($link_cmd == $eqLogic_cmd->getName()) {
						$cmd = cmd::byId($cmd_id);
						if (is_object($cmd)) {
							$cmd->setValue($eqLogic_cmd->getId());
							$cmd->save();
						}
					}
				}
			}
		}
		if (count($link_actions) > 0) {
			foreach ($this->getCmd() as $eqLogic_cmd) {
				foreach ($link_actions as $cmd_id => $link_action) {
					if ($link_action == $eqLogic_cmd->getName()) {
						$cmd = cmd::byId($cmd_id);
						if (is_object($cmd)) {
							$cmd->setConfiguration('updateCmdId', $eqLogic_cmd->getId());
							$cmd->save();
						}
					}
				}
			}
		}
		$this->save();
	}
/*     * **********************Getteur Setteur*************************** */
}
class edisioCmd extends cmd {
	/*     * *************************Attributs****************************** */
	/*     * ***********************Methode static*************************** */
	/*     * *********************Methode d'instance************************* */
	public function execute($_options = null) {
		if ($this->getType() != 'action') {
			return;
		}
		$eqLogic = $this->getEqLogic();
		$logicalId = ($this->getConfiguration('id') != '') ? $this->getConfiguration('id') : $eqLogic->getLogicalId();
		$value = trim(str_replace("#ID#", $logicalId, $this->getLogicalId()));
		$group = $this->getConfiguration('group', '01');
		if (strlen($group) == 1) {
			$group = '0' . $group;
		}
		$value = trim(str_replace("#GROUP#", $group, $value));
		switch ($this->getSubType()) {
			case 'slider':
				$hexvalue = strtoupper(dechex(intval($_options['slider'])));
				if (strlen($hexvalue) < 2) {
					$hexvalue = '0' . $hexvalue;
				}
				if ($hexvalue != '00') {
					$value = str_replace('#slider#', $hexvalue, $value);
				} else {
					$value = str_replace('04#slider#', '02', $value);
				}
				break;
			case 'color':
				$value = str_replace('#color#', $_options['color'], $value);
				break;
		}
		$values = explode('&&', $value);
		$message = trim(json_encode(array('apikey' => jeedom::getApiKey('edisio'), 'cmd' => 'send', 'data' => $values)));
		$socket = socket_create(AF_INET, SOCK_STREAM, 0);
		socket_connect($socket, '127.0.0.1', config::byKey('socketport', 'edisio'));
		socket_write($socket, $message, strlen($message));
		socket_close($socket);
	}
	/*     * **********************Getteur Setteur*************************** */
}
?>