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
if (!isConnect()) {
	include_file('desktop', '404', 'php');
	die();
}
?>
<form class="form-horizontal">
    <fieldset>
     <legend><i class="fa fa-list-alt"></i> {{Générale}}</legend>
     <div class="form-group">
        <label class="col-lg-4 control-label">{{Bannir les IDs}}</label>
        <div class="col-lg-8">
            <textarea class="configKey form-control" data-l1key="banEdisioId" rows="3"/>
        </div>
    </div>
    <legend><i class="icon loisir-darth"></i> {{Démon local}}</legend>
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
       <label class="col-lg-4 control-label">{{Enregistrer tous les messages, cela peut ralentir le système}}</label>
       <div class="col-lg-1">
        <input type="checkbox" class="configKey bootstrapSwitch" data-l1key="enableLogging" />
    </div>
    <div class="col-lg-7">
        <a class="btn btn-default" id="bt_logEdisioMessage"><i class="fa fa-file-o"></i> {{Voir les messages}}</a>
    </div>
</div>
<div class="form-group expertModeVisible">
    <label class="col-lg-4 control-label">{{Port socket interne (modification dangereuse, doit etre le meme surtout les esclaves)}}</label>
    <div class="col-lg-2">
        <input class="configKey form-control" data-l1key="socketport" value='55005' />
    </div>
</div>
<div class="form-group">
    <label class="col-sm-4 control-label">{{Traiter la répétition des messages}}</label>
    <div class="col-sm-2">
        <input type="checkbox" class="configKey bootstrapSwitch" data-l1key="processRepeatMessage" />
    </div>
</div>
<div class="form-group">
    <label class="col-sm-4 control-label">{{Forcer la répétition des messages toutes les (min)}}</label>
    <div class="col-sm-2">
        <input class="configKey form-control" data-l1key="repeatMessageTime" />
    </div>
</div>
</fieldset>
</form>

<?php
if (config::byKey('jeeNetwork::mode') == 'master') {
	foreach (jeeNetwork::byPlugin('edisio') as $jeeNetwork) {
		?>
        <form class="form-horizontal slaveConfig" data-slave_id="<?php echo $jeeNetwork->getId(); ?>">
            <fieldset>
                <legend><i class="icon loisir-darth"></i> {{Démon sur l'esclave}} <?php echo $jeeNetwork->getName() ?></legend>
                <div class="form-group">
                    <label class="col-lg-4 control-label">{{Port Edisio}}</label>
                    <div class="col-lg-4">
                        <select class="slaveConfigKey form-control" data-l1key="port">
                            <option value="none">{{Aucun}}</option>
                            <option value="auto">{{Auto}}</option>
                            <?php
foreach ($jeeNetwork->sendRawRequest('jeedom::getUsbMapping') as $name => $value) {
			echo '<option value="' . $name . '">' . $name . ' (' . $value . ')</option>';
		}
		?>
                     </select>
                 </div>
             </div>
             <div class="form-group">
               <label class="col-lg-4 control-label">{{Enregistrer tous les messages, cela peut ralentir le système}}</label>
               <div class="col-lg-1">
                <input type="checkbox" class="slaveConfigKey bootstrapSwitch" data-l1key="enableLogging" />
            </div>
            <div class="col-lg-7">
                <a class="btn btn-default bt_logEdisioMessage"><i class="fa fa-file-o"></i> {{Voir les messages}}</a>
            </div>
        </div>
        <div class="form-group expertModeVisible">
            <label class="col-lg-4 control-label">{{Port socket interne (modification dangereuse, doit etre le meme surtout les esclaves)}}</label>
            <div class="col-lg-2">
                <input class="slaveConfigKey form-control" data-l1key="socketport" value='55005' />
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-4 control-label">{{Traiter la répétition des messages}}</label>
            <div class="col-sm-2">
                <input type="checkbox" class="slaveConfigKey bootstrapSwitch" data-l1key="processRepeatMessage" />
            </div>
        </div>
        <div class="form-group">
            <label class="col-sm-4 control-label">{{Forcer la répétition des messages toutes les (min)}}</label>
            <div class="col-sm-2">
                <input class="slaveConfigKey form-control" data-l1key="repeatMessageTime" />
            </div>
        </div>
    </fieldset>
</form>

<?php
}
}
?>


<script>
 $('.bt_logEdisioMessage').on('click', function () {
   var slave_id = $(this).closest('.slaveConfig').attr('data-slave_id');
   $('#md_modal').dialog({title: "{{Log des messages Edisio}}"});
   $('#md_modal').load('index.php?v=d&plugin=edisio&modal=show.log&slave_id='+slave_id).dialog('open');
});

 $('#bt_logEdisioMessage').on('click', function () {
    $('#md_modal').dialog({title: "{{Log des messages EDISIO}}"});
    $('#md_modal').load('index.php?v=d&plugin=edisio&modal=show.log').dialog('open');
});
</script>