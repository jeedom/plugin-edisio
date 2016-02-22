<?php
if (!isConnect('admin')) {
	throw new Exception('Error 401 Unauthorized');
}
sendVarToJS('eqType', 'edisio');
$eqLogics = eqLogic::byType('edisio');
sendVarToJS('marketAddr', config::byKey('market::address'));
function sortByOption($a, $b) {
	return strcmp($a['name'], $b['name']);
}
if (config::byKey('autoDiscoverEqLogic', 'rfxcom', 0) == 1) {
	echo '<div class="alert jqAlert alert-warning" id="div_inclusionAlert" style="margin : 0px 5px 15px 15px; padding : 7px 35px 7px 15px;">{{Vous etes en mode inclusion. Recliquez sur le bouton d\'inclusion pour sortir de ce mode}}</div>';
} else {
	echo '<div id="div_inclusionAlert"></div>';
}
?>

<div class="row row-overflow">
  <div class="col-lg-2 col-md-3 col-sm-4">
    <div class="bs-sidebar">
      <ul id="ul_eqLogic" class="nav nav-list bs-sidenav">
        <a class="btn btn-default eqLogicAction" style="width : 100%;margin-top : 5px;margin-bottom: 5px;" data-action="add"><i class="fa fa-plus-circle"></i> {{Ajouter}}</a>
        <li class="filter" style="margin-bottom: 5px;"><input class="filter form-control input-sm" placeholder="Rechercher" style="width: 100%"/></li>
        <?php
foreach ($eqLogics as $eqLogic) {
	$opacity = ($eqLogic->getIsEnable()) ? '' : jeedom::getConfiguration('eqLogic:style:noactive');
	echo '<li class="cursor li_eqLogic" data-eqLogic_id="' . $eqLogic->getId() . '" style="' . $opacity . '"><a>' . $eqLogic->getHumanName(true) . '</a></li>';
}
?>
     </ul>
   </div>
 </div>

 <div class="col-lg-10 col-md-9 col-sm-8 eqLogicThumbnailDisplay" style="border-left: solid 1px #EEE; padding-left: 25px;">
   <legend><i class="fa fa-cog"></i>  {{Gestion}}</legend>
   <div class="eqLogicThumbnailContainer">
     <div class="cursor eqLogicAction" data-action="add" style="background-color : #ffffff; height : 120px;margin-bottom : 10px;padding : 5px;border-radius: 2px;width : 160px;margin-left : 10px;" >
       <center>
        <i class="fa fa-plus-circle" style="font-size : 5em;color:#94ca02;"></i>
      </center>
      <span style="font-size : 1.1em;position:relative; top : 15px;word-break: break-all;white-space: pre-wrap;word-wrap: break-word;color:#94ca02"><center>{{Ajouter}}</center></span>
    </div>
    <?php
if (config::byKey('autoDiscoverEqLogic', 'edisio', 0) == 1) {
	echo '<div class="cursor changeIncludeState card" data-mode="1" data-state="0" style="background-color : #8000FF; height : 140px;margin-bottom : 10px;padding : 5px;border-radius: 2px;width : 160px;margin-left : 10px;" >';
	echo '<center>';
	echo '<i class="fa fa-sign-in fa-rotate-90" style="font-size : 5em;color:#94ca02;"></i>';
	echo '</center>';
	echo '<span style="font-size : 1.1em;position:relative; top : 15px;word-break: break-all;white-space: pre-wrap;word-wrap: break-word;color:#94ca02"><center>{{Arrêter inclusion}}</center></span>';
	echo '</div>';
} else {
	echo '<div class="cursor changeIncludeState card" data-mode="1" data-state="1" style="background-color : #ffffff; height : 140px;margin-bottom : 10px;padding : 5px;border-radius: 2px;width : 160px;margin-left : 10px;" >';
	echo '<center>';
	echo '<i class="fa fa-sign-in fa-rotate-90" style="font-size : 5em;color:#94ca02;"></i>';
	echo '</center>';
	echo '<span style="font-size : 1.1em;position:relative; top : 15px;word-break: break-all;white-space: pre-wrap;word-wrap: break-word;color:#94ca02"><center>{{Mode inclusion}}</center></span>';
	echo '</div>';
}
?>
   <div class="cursor eqLogicAction" data-action="gotoPluginConf" style="background-color : #ffffff; height : 120px;margin-bottom : 10px;padding : 5px;border-radius: 2px;width : 160px;margin-left : 10px;">
    <center>
      <i class="fa fa-wrench" style="font-size : 5em;color:#767676;"></i>
    </center>
    <span style="font-size : 1.1em;position:relative; top : 15px;word-break: break-all;white-space: pre-wrap;word-wrap: break-word;color:#767676"><center>{{Configuration}}</center></span>
  </div>
  <div class="cursor" id="bt_healthEdisio" style="background-color : #ffffff; height : 120px;margin-bottom : 10px;padding : 5px;border-radius: 2px;width : 160px;margin-left : 10px;" >
    <center>
      <i class="fa fa-medkit" style="font-size : 5em;color:#767676;"></i>
    </center>
    <span style="font-size : 1.1em;position:relative; top : 15px;word-break: break-all;white-space: pre-wrap;word-wrap: break-word;color:#767676"><center>{{Santé}}</center></span>
  </div>
</div>
<legend><i class="fa fa-table"></i> {{Mes équipements EDISIO}}</legend>
<div class="eqLogicThumbnailContainer">

  <?php
foreach ($eqLogics as $eqLogic) {
	$opacity = ($eqLogic->getIsEnable()) ? '' : jeedom::getConfiguration('eqLogic:style:noactive');
	echo '<div class="eqLogicDisplayCard cursor" data-eqLogic_id="' . $eqLogic->getId() . '" style="background-color : #ffffff; height : 200px;margin-bottom : 10px;padding : 5px;border-radius: 2px;width : 160px;margin-left : 10px;' . $opacity . '" >';
	echo "<center>";
	$alternateImg = $eqLogic->getConfiguration('iconModel');
	if (file_exists(dirname(__FILE__) . '/../../core/config/devices/' . $alternateImg . '.jpg')) {
		echo '<img class="lazy" src="plugins/edisio/core/config/devices/' . $alternateImg . '.jpg" height="105" width="95" />';
	} elseif (file_exists(dirname(__FILE__) . '/../../core/config/devices/' . $eqLogic->getConfiguration('device') . '.jpg')) {
		echo '<img class="lazy" src="plugins/edisio/core/config/devices/' . $eqLogic->getConfiguration('device') . '.jpg" height="105" width="95" />';
	} else {
		echo '<img class="lazy" src="plugins/edisio/doc/images/edisio_icon.png" height="105" width="95" />';
	}
	echo "</center>";
	echo '<span style="font-size : 1.1em;position:relative; top : 15px;word-break: break-all;white-space: pre-wrap;word-wrap: break-word;"><center>' . $eqLogic->getHumanName(true, true) . '</center></span>';
	echo '</div>';
}
?>
</div>
</div>

<div class="col-lg-10 col-md-9 col-sm-8 eqLogic" style="border-left: solid 1px #EEE; padding-left: 25px;display: none;">
  <div class="row">
    <div class="col-sm-6">
      <form class="form-horizontal">
        <fieldset>
          <legend><i class="fa fa-arrow-circle-left eqLogicAction cursor" data-action="returnToThumbnailDisplay"></i> {{Général}}
            <i class='fa fa-cogs eqLogicAction pull-right cursor expertModeVisible' data-action='configure'></i>
            <a class="btn btn-xs btn-default pull-right eqLogicAction" data-action="copy"><i class="fa fa-files-o"></i> {{Dupliquer}}</a>
          </legend>
          <div class="form-group">
            <label class="col-sm-3 control-label">{{Nom de l'équipement EDISIO}}</label>
            <div class="col-sm-4">
              <input type="text" class="eqLogicAttr form-control" data-l1key="id" style="display : none;" />
              <input type="text" class="eqLogicAttr form-control" data-l1key="name" placeholder="Nom de l'équipement EDISIO"/>
            </div>
          </div>
          <div class="form-group">
            <label class="col-sm-3 control-label">{{ID}}</label>
            <div class="col-sm-4">
              <input type="text" class="eqLogicAttr form-control" data-l1key="logicalId" placeholder="Logical ID"/>
            </div>
          </div>
          <div class="form-group">
            <label class="col-sm-3 control-label"></label>
            <div class="col-sm-9">
             <input type="checkbox" class="eqLogicAttr bootstrapSwitch" data-label-text="{{Activer}}" data-l1key="isEnable" checked/>
             <input type="checkbox" class="eqLogicAttr bootstrapSwitch" data-label-text="{{Visible}}" data-l1key="isVisible" checked/>
           </div>
         </div>
         <div class="form-group">
          <label class="col-sm-3 control-label" >{{Objet parent}}</label>
          <div class="col-sm-4">
            <select class="eqLogicAttr form-control" data-l1key="object_id">
              <option value="">{{Aucun}}</option>
              <?php
foreach (object::all() as $object) {
	echo '<option value="' . $object->getId() . '">' . $object->getName() . '</option>';
}
?>
           </select>
         </div>
       </div>
       <div class="form-group">
        <label class="col-sm-3 control-label">{{Catégorie}}</label>
        <div class="col-sm-9">
          <?php
foreach (jeedom::getConfiguration('eqLogic:category') as $key => $value) {
	echo '<label class="checkbox-inline">';
	echo '<input type="checkbox" class="eqLogicAttr" data-l1key="category" data-l2key="' . $key . '" />' . $value['name'];
	echo '</label>';
}
?>

       </div>
     </div>
     <div class="form-group expertModeVisible">
      <label class="col-sm-3 control-label">{{Ne pas verifier la batterie}}</label>
      <div class="col-sm-1">
        <input type="checkbox" class="eqLogicAttr bootstrapSwitch" data-l1key="configuration" data-l2key="noBatterieCheck"/>
      </div>
    </div>
    <div class="form-group expertModeVisible">
      <label class="col-sm-3 control-label">{{Délai maximum autorisé entre 2 messages (min)}}</label>
      <div class="col-sm-4">
        <input class="eqLogicAttr form-control" data-l1key="timeout" />
      </div>
    </div>
    <div class="form-group">
      <label class="col-sm-3 control-label">{{Commentaire}}</label>
      <div class="col-sm-8">
        <textarea class="eqLogicAttr form-control" data-l1key="configuration" data-l2key="commentaire" ></textarea>
      </div>
    </div>
  </fieldset>
</form>
</div>
<div class="col-sm-6">
  <form class="form-horizontal">
    <fieldset>
      <legend><i class="fa fa-info-circle"></i>  {{Informations}}</legend>
      <div class="form-group">
        <label class="col-sm-3 control-label">{{Equipement}}</label>
        <div class="col-sm-6">
         <select class="eqLogicAttr form-control" data-l1key="configuration" data-l2key="device">
          <option value="">{{Aucun}}</option>
          <?php
$groups = array();

foreach (edisio::devicesParameters() as $key => $info) {
	if (isset($info['groupe'])) {
		$info['key'] = $key;
		if (!isset($groups[$info['groupe']])) {
			$groups[$info['groupe']][0] = $info;
		} else {
			array_push($groups[$info['groupe']], $info);
		}
	}
}
ksort($groups);
foreach ($groups as $group) {
	usort($group, function ($a, $b) {
		return strcmp($a['name'], $b['name']);
	});
	foreach ($group as $key => $info) {
		if ($key == 0) {
			echo '<optgroup label="{{' . $info['groupe'] . '}}">';
		}
		echo '<option value="' . $info['key'] . '">' . $info['name'] . '</option>';
	}
	echo '</optgroup>';
}
?>
   </select>
 </div>
</div>
<div class="form-group expertModeVisible">
  <label class="col-sm-3 control-label">{{Création}}</label>
  <div class="col-sm-3">
    <span class="eqLogicAttr label label-default" data-l1key="configuration" data-l2key="createtime" style="font-size : 1em;cursor : default;"></span>
  </div>
  <label class="col-sm-3 control-label">{{Statut}}</label>
  <div class="col-sm-2">
    <span class="eqLogicAttr label label-default tooltips" data-l1key="status" data-l2key="state" style="font-size : 1em;cursor : default;"></span>
  </div>
</div>
<div class="form-group expertModeVisible">
  <label class="col-sm-3 control-label hasCommunication">{{Communication}}</label>
  <div class="col-sm-3 hasCommunication">
    <span class="eqLogicAttr label label-default" data-l1key="status" data-l2key="lastCommunication" style="font-size : 1em;cursor : default;"></span>
  </div>
  <label class="col-sm-3 control-label hasBatterie">{{Batterie}}</label>
  <div class="col-sm-3 hasBatterie">
    <span class="eqLogicAttr label label-default tooltips" data-l1key="configuration" data-l2key="batteryStatus" style="font-size : 1em;cursor : default;"></span> %
  </div>
</div>
<div class="form-group modelList" style="display:none;">
  <label class="col-sm-3 control-label">{{Modèle}}</label>
  <div class="col-sm-6">
   <select class="eqLogicAttr form-control listModel" data-l1key="configuration" data-l2key="iconModel">
   </select>
 </div>
</div>
<center>
  <img src="core/img/no_image.gif" data-original=".jpg" id="img_device" class="img-responsive" style="max-height : 250px;" onerror="this.src='plugins/edisio/doc/images/edisio_icon.png'"/>
</center>
</fieldset>
</form>
</div>
</div>

<form class="form-horizontal">
  <fieldset>
    <div class="form-actions" align="right">
      <a class="btn btn-danger eqLogicAction" data-action="remove"><i class="fa fa-minus-circle"></i> {{Supprimer}}</a>
      <a class="btn btn-success eqLogicAction" data-action="save"><i class="fa fa-check-circle"></i> {{Sauvegarder}}</a>
    </div>
  </fieldset>
</form>

<legend><i class="fa fa-list-alt"></i> {{Commandes}}</legend>


<a class="btn btn-success btn-sm cmdAction" data-action="add"><i class="fa fa-plus-circle"></i> {{Ajouter une commande}}</a><br/><br/>
<table id="table_cmd" class="table table-bordered table-condensed">
  <thead>
    <tr>
      <th style="width: 300px;">{{Nom}}</th>
      <th style="width: 130px;" class="expertModeVisible">{{Type}}</th>
      <th class="expertModeVisible">{{Logical ID (info) ou Commande brute (action)}}</th>
      <th>{{Paramètres}}</th>
      <th style="width: 100px;">{{Options}}</th>
      <th></th>
    </tr>
  </thead>
  <tbody>

  </tbody>
</table>

<form class="form-horizontal">
  <fieldset>
    <div class="form-actions">
      <a class="btn btn-danger eqLogicAction" data-action="remove"><i class="fa fa-minus-circle"></i> {{Supprimer}}</a>
      <a class="btn btn-success eqLogicAction" data-action="save"><i class="fa fa-check-circle"></i> {{Sauvegarder}}</a>
    </div>
  </fieldset>
</form>

</div>
</div>

<?php include_file('desktop', 'edisio', 'js', 'edisio');?>
<?php include_file('core', 'plugin.template', 'js');?>
