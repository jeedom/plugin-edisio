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
include_file('core', 'authentification', 'php');
if (!isConnect('admin')) {
	throw new Exception('{{401 - Accès non autorisé}}');
}
?>
<form class="form-horizontal">
  <fieldset>
   <legend><i class="fa fa-list-alt"></i> {{Générale}}</legend>
   <div class="form-group">
    <label class="col-lg-4 control-label">{{Bannir les IDs}}</label>
    <div class="col-lg-8">
      <textarea class="configKey form-control" data-l1key="banEdisioId" rows="3" ></textarea>
    </div>
  </div>
</fieldset>
</form>
<form class="form-horizontal">
  <fieldset>
  <legend><i class="icon loisir-darth"></i> {{Démon}}</legend>
    <div class="form-group">
      <label class="col-lg-4 control-label">{{Port EDISIO}}</label>
      <div class="col-lg-4">
        <select class="configKey form-control" data-l1key="port">
          <option value="none">{{Aucun}}</option>
          <option value="auto">{{Auto}}</option>
          <?php
foreach (jeedom::getUsbMapping() as $name => $value) {
	echo '<option value="' . $name . '">' . $name . ' (' . $value . ')</option>';
}
?>
       </select>
     </div>
   </div>
   <div class="form-group">
    <label class="col-lg-4 control-label">{{Port socket interne}}</label>
    <div class="col-lg-2">
      <input class="configKey form-control" data-l1key="socketport"/>
    </div>
  </div>
  <div class="form-group">
    <label class="col-sm-4 control-label">{{Cycle (s)}}</label>
    <div class="col-sm-2">
      <input class="configKey form-control" data-l1key="cycle" />
    </div>
  </div>
</fieldset>
</form>
