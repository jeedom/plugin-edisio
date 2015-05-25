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
$port = config::byKey('port', 'edisio');
$deamonRunningMaster = edisio::deamonRunning();
$deamonRunningSlave = array();
if (config::byKey('jeeNetwork::mode') == 'master') {
	foreach (jeeNetwork::byPlugin('edisio') as $jeeNetwork) {
		try {
			$deamonRunningSlave[$jeeNetwork->getName()] = $jeeNetwork->sendRawRequest('deamonRunning', array('plugin' => 'edisio'));
		} catch (Exception $e) {
			$deamonRunningSlave[$jeeNetwork->getName()] = false;
		}
	}
}
?>


<form class="form-horizontal">
    <fieldset>
        <?php
echo '<div class="form-group">';
echo '<label class="col-sm-4 control-label">{{Démon local}}</label>';
if (!$deamonRunningMaster) {
	echo '<div class="col-sm-1"><span class="label label-danger tooltips" title="{{Peut être normale si vous etes en deporté}}">NOK</span></div>';
} else {
	echo '<div class="col-sm-1"><span class="label label-success">OK</span></div>';
}
echo '</div>';
foreach ($deamonRunningSlave as $name => $status) {
	echo ' <div class="form-group"><label class="col-sm-4 control-label">{{Sur l\'esclave}} ' . $name . '</label>';
	if (!$status) {
		echo '<div class="col-sm-1"><span class="label label-danger">NOK</span></div>';
	} else {
		echo '<div class="col-sm-1"><span class="label label-success">OK</span></div>';
	}
	echo '</div>';
}
?>
  </fieldset>
</form>
<form class="form-horizontal">
    <fieldset>
       <legend>{{Générale}}</legend>
       <div class="form-group">
        <label class="col-lg-4 control-label">{{Créer automatiquement les nouveaux équipements}}</label>
        <div class="col-lg-4">
            <input type="checkbox" class="configKey" data-l1key="autoDiscoverEqLogic" />
        </div>
    </div>
    <div class="form-group">
        <label class="col-lg-4 control-label">{{Bannir les IDs}}</label>
        <div class="col-lg-8">
            <textarea class="configKey form-control" data-l1key="banEdisioId" rows="3"/>
        </div>
    </div>
    <legend>{{Démon local}}</legend>
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
        <input type="checkbox" class="configKey" data-l1key="enableLogging" />
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
        <input type="checkbox" class="configKey" data-l1key="processRepeatMessage" />
    </div>
</div>
<div class="form-group">
    <label class="col-sm-4 control-label">{{Forcer la répétition des messages toutes les (min)}}</label>
    <div class="col-sm-2">
        <input class="configKey form-control" data-l1key="repeatMessageTime" />
    </div>
</div>
<div class="form-group">
    <label class="col-lg-4 control-label">{{Gestion du démon}}</label>
    <div class="col-lg-8">
        <a class="btn btn-success" id="bt_restartEdisioDeamon"><i class='fa fa-play'></i> {{(Re)démarrer}}</a>
        <a class="btn btn-danger" id="bt_stopEdisioDeamon"><i class='fa fa-stop'></i> {{Arrêter}}</a>
        <a class="btn btn-warning" id="bt_launchEdisioInDebug"><i class="fa fa-exclamation-triangle"></i> {{Lancer en mode debug}}</a>
    </div>
</div>
</fieldset>
</form>

<?php
if (config::byKey('jeeNetwork::mode') == 'master') {
	foreach (jeeNetwork::byPlugin('edisio') as $jeeNetwork) {
		?>
        <form class="form-horizontal slaveConfig" data-slave_id="<?php echo $jeeNetwork->getId();?>">
            <fieldset>
                <legend>{{Démon sur l'esclave}} <?php echo $jeeNetwork->getName()?></legend>
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
                    <input type="checkbox" class="slaveConfigKey" data-l1key="enableLogging" />
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
                    <input type="checkbox" class="slaveConfigKey" data-l1key="processRepeatMessage" />
                </div>
            </div>
            <div class="form-group">
                <label class="col-sm-4 control-label">{{Forcer la répétition des messages toutes les (min)}}</label>
                <div class="col-sm-2">
                    <input class="slaveConfigKey form-control" data-l1key="repeatMessageTime" />
                </div>
            </div>
            <div class="form-group">
                <label class="col-lg-4 control-label">{{Gestion du démon}}</label>
                <div class="col-lg-8">
                    <a class="btn btn-success bt_restartEdisioDeamon"><i class='fa fa-play'></i> {{(Re)démarrer}}</a>
                    <a class="btn btn-danger bt_stopEdisioDeamon"><i class='fa fa-stop'></i> {{Arrêter}}</a>
                    <a class="btn btn-warning bt_launchEdisioInDebug"><i class="fa fa-exclamation-triangle"></i> {{Lancer en mode debug}}</a>
                </div>
            </div>
        </fieldset>
    </form>

    <?php
}
}
?>


<script>
   $('.bt_restartEdisioDeamon').on('click', function () {
        $.ajax({// fonction permettant de faire de l'ajax
            type: "POST", // methode de transmission des données au fichier php
            url: "plugins/edisio/core/ajax/edisio.ajax.php", // url du fichier php
            data: {
                action: "restartSlaveDeamon",
                id : $(this).closest('.slaveConfig').attr('data-slave_id')
            },
            dataType: 'json',
            error: function (request, status, error) {
                handleAjaxError(request, status, error);
            },
            success: function (data) { // si l'appel a bien fonctionné
            if (data.state != 'ok') {
                $('#div_alert').showAlert({message: data.result, level: 'danger'});
                return;
            }
            $('#div_alert').showAlert({message: '{{Le démon a été correctement (re)demarré}}', level: 'success'});
            $('#ul_plugin .li_plugin[data-plugin_id=edisio]').click();
        }
    });
    });

   $('.bt_stopEdisioDeamon').on('click', function () {
        $.ajax({// fonction permettant de faire de l'ajax
            type: "POST", // methode de transmission des données au fichier php
            url: "plugins/edisio/core/ajax/edisio.ajax.php", // url du fichier php
            data: {
                action: "stopSlaveDeamon",
                id : $(this).closest('.slaveConfig').attr('data-slave_id')
            },
            dataType: 'json',
            error: function (request, status, error) {
                handleAjaxError(request, status, error);
            },
            success: function (data) { // si l'appel a bien fonctionné
            if (data.state != 'ok') {
                $('#div_alert').showAlert({message: data.result, level: 'danger'});
                return;
            }
            $('#div_alert').showAlert({message: '{{Le démon a été correctement arreté}}', level: 'success'});
            $('#ul_plugin .li_plugin[data-plugin_id=edisio]').click();
        }
    });
    });

   $('.bt_launchEdisioInDebug').on('click', function () {
    var slave_id = $(this).closest('.slaveConfig').attr('data-slave_id');
    bootbox.confirm('{{Etes-vous sur de vouloir lancer le démon en mode debug ? N\'oubliez pas de le relancer en mode normale une fois terminé}}', function (result) {
        if (result) {
            $('#md_modal').dialog({title: "{{Edisio en mode debug}}"});
            $('#md_modal').load('index.php?v=d&plugin=edisio&modal=show.debug&slave_id='+slave_id).dialog('open');
        }
    });
});


   $('#bt_restartEdisioDeamon').on('click', function () {
        $.ajax({// fonction permettant de faire de l'ajax
            type: "POST", // methode de transmission des données au fichier php
            url: "plugins/edisio/core/ajax/edisio.ajax.php", // url du fichier php
            data: {
                action: "restartDeamon",
            },
            dataType: 'json',
            error: function (request, status, error) {
                handleAjaxError(request, status, error);
            },
            success: function (data) { // si l'appel a bien fonctionné
            if (data.state != 'ok') {
                $('#div_alert').showAlert({message: data.result, level: 'danger'});
                return;
            }
            $('#div_alert').showAlert({message: '{{Le démon a été correctement (re)démarré}}', level: 'success'});
            $('#ul_plugin .li_plugin[data-plugin_id=edisio]').click();
        }
    });
    });

   $('#bt_stopEdisioDeamon').on('click', function () {
        $.ajax({// fonction permettant de faire de l'ajax
            type: "POST", // methode de transmission des données au fichier php
            url: "plugins/edisio/core/ajax/edisio.ajax.php", // url du fichier php
            data: {
                action: "stopDeamon",
            },
            dataType: 'json',
            error: function (request, status, error) {
                handleAjaxError(request, status, error);
            },
            success: function (data) { // si l'appel a bien fonctionné
            if (data.state != 'ok') {
                $('#div_alert').showAlert({message: data.result, level: 'danger'});
                return;
            }
            $('#div_alert').showAlert({message: '{{Le démon a été correctement arrêté}}', level: 'success'});
            $('#ul_plugin .li_plugin[data-plugin_id=edisio]').click();
        }
    });
    });

   $('#bt_manageEdisioComProtocole').on('click', function () {
    $('#md_modal').dialog({title: "{{Gestion des protocoles EDISIO}}"});
    $('#md_modal').load('index.php?v=d&plugin=edisio&modal=manage.protocole').dialog('open');
});

   $('.bt_logEdisioMessage').on('click', function () {
     var slave_id = $(this).closest('.slaveConfig').attr('data-slave_id');
     $('#md_modal').dialog({title: "{{Log des messages Edisio}}"});
     $('#md_modal').load('index.php?v=d&plugin=edisio&modal=show.log&slave_id='+slave_id).dialog('open');
 });

   $('#bt_logEdisioMessage').on('click', function () {
    $('#md_modal').dialog({title: "{{Log des messages EDISIO}}"});
    $('#md_modal').load('index.php?v=d&plugin=edisio&modal=show.log').dialog('open');
});

   $('#bt_launchEdisioInDebug').on('click', function () {
    bootbox.confirm('{{Etes-vous sur de vouloir lancer le démon en mode debug ? N\'oubliez pas d\arrêter/redemarrer le démon une fois terminé}}', function (result) {
        if (result) {
            $('#md_modal').dialog({title: "{{EDISIO en mode debug}}"});
            $('#md_modal').load('index.php?v=d&plugin=edisio&modal=show.debug').dialog('open');
        }
    });
});

   function edisio_postSaveConfiguration(){
             $.ajax({// fonction permettant de faire de l'ajax
            type: "POST", // methode de transmission des données au fichier php
            url: "plugins/edisio/core/ajax/edisio.ajax.php", // url du fichier php
            data: {
                action: "restartDeamon",
            },
            dataType: 'json',
            error: function (request, status, error) {
                handleAjaxError(request, status, error);
            },
            success: function (data) { // si l'appel a bien fonctionné
            if (data.state != 'ok') {
                $('#div_alert').showAlert({message: data.result, level: 'danger'});
                return;
            }
        }
    });
         }



         function edisio_postSaveSlaveConfiguration(_slave_id){
             $.ajax({// fonction permettant de faire de l'ajax
            type: "POST", // methode de transmission des données au fichier php
            url: "plugins/edisio/core/ajax/edisio.ajax.php", // url du fichier php
            data: {
                action: "restartSlaveDeamon",
                id : _slave_id
            },
            dataType: 'json',
            error: function (request, status, error) {
                handleAjaxError(request, status, error);
            },
            success: function (data) { // si l'appel a bien fonctionné
            if (data.state != 'ok') {
                $('#div_alert').showAlert({message: data.result, level: 'danger'});
                return;
            }
        }
    });
         }
     </script>