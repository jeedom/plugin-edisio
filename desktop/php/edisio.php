<?php
if (!isConnect('admin')) {
	throw new Exception('Error 401 Unauthorized');
}
$plugin = plugin::byId('edisio');
sendVarToJS('eqType', $plugin->getId());
$eqLogics = eqLogic::byType($plugin->getId());
function sortByOption($a, $b) {
	return strcmp($a['name'], $b['name']);
}
if (config::byKey('include_mode', 'edisio', 0) == 1) {
	echo '<div class="alert jqAlert alert-warning" id="div_inclusionAlert" style="margin : 0px 5px 15px 15px; padding : 7px 35px 7px 15px;">{{Vous etes en mode inclusion. Recliquez sur le bouton d\'inclusion pour sortir de ce mode}}</div>';
} else {
	echo '<div id="div_inclusionAlert"></div>';
}
?>

<div class="row row-overflow">
 <div class="col-lg-12 eqLogicThumbnailDisplay">
   <legend><i class="fa fa-cog"></i>  {{Gestion}}</legend>
   <div class="eqLogicThumbnailContainer">
	<div class="cursor eqLogicAction logoPrimary" data-action="add">
		<i class="fas fa-plus-circle"></i>
		<br/>
		<span>{{Ajouter}}</span>
	</div>
    <?php
if (config::byKey('include_mode', 'edisio', 0) == 1) {
	echo '<div class="cursor changeIncludeState include card logoSecondary" data-mode="1" data-state="0">';
	echo '<i class="fas fa-sign-in-alt fa-rotate-90"></i>';
	echo '<br/>';
	echo '<span>{{Arrêter inclusion}}</span>';
	echo '</div>';
} else {
	echo '<div class="cursor changeIncludeState include card logoSecondary" data-mode="1" data-state="1">';
	echo '<i class="fas fa-sign-in-alt fa-rotate-90"></i>';
	echo '<br/>';
	echo '<span>{{Mode inclusion}}</span>';
	echo '</div>';
}
?>
	<div class="cursor eqLogicAction logoSecondary" data-action="gotoPluginConf">
		<i class="fas fa-wrench"></i>
		<br/>
		<span>{{Configuration}}</span>
	</div>
  <div class="cursor logoSecondary" id="bt_healthEdisio">
	<i class="fas fa-medkit"></i>
	<br/>
	<span>{{Santé}}</span>
  </div>
</div>
<legend><i class="fa fa-table"></i> {{Mes équipements EDISIO}}</legend>
<input class="form-control" placeholder="{{Rechercher}}" id="in_searchEqlogic" />
<div class="eqLogicThumbnailContainer">
  <?php
foreach ($eqLogics as $eqLogic) {
	$opacity = ($eqLogic->getIsEnable()) ? '' : 'disableCard';
	echo '<div class="eqLogicDisplayCard cursor '.$opacity.'" data-eqLogic_id="' . $eqLogic->getId() . '" >';
	$alternateImg = $eqLogic->getConfiguration('iconModel');
	if (file_exists(dirname(__FILE__) . '/../../core/config/devices/'.$eqLogic->getConfiguration('device').'/'. $alternateImg . '.jpg')) {
		echo '<img class="lazy" src="plugins/edisio/core/config/devices/'.$eqLogic->getConfiguration('device').'/' . $alternateImg . '.jpg" height="105" width="95" />';
	} elseif (file_exists(dirname(__FILE__) . '/../../core/config/devices/' .  $eqLogic->getConfiguration('device') . '/' .$eqLogic->getConfiguration('device') . '.jpg')) {
		echo '<img class="lazy" src="plugins/edisio/core/config/devices/' . $eqLogic->getConfiguration('device') . '/' . $eqLogic->getConfiguration('device') . '.jpg" height="105" width="95" />';
	} else {
		echo '<img src="' . $plugin->getPathImgIcon() . '" height="105" width="95" />';
	}
	echo '<br/>';
	echo '<span class="name">' . $eqLogic->getHumanName(true, true) . '</span>';
	echo '</div>';
}
?>
</div>
</div>

<div class="col-xs-12 eqLogic" style="display: none;">
 	<div class="input-group pull-right" style="display:inline-flex">
			<span class="input-group-btn">
				<a class="btn btn-default btn-sm eqLogicAction roundedLeft" data-action="configure"><i class="fas fa-cogs"></i> {{Configuration avancée}}</a><a class="btn btn-default btn-sm eqLogicAction" data-action="copy"><i class="fas fa-copy"></i> {{Dupliquer}}</a><a class="btn btn-sm btn-success eqLogicAction" data-action="save"><i class="fas fa-check-circle"></i> {{Sauvegarder}}</a><a class="btn btn-danger btn-sm eqLogicAction roundedRight" data-action="remove"><i class="fas fa-minus-circle"></i> {{Supprimer}}</a>
			</span>
		</div>
  <ul class="nav nav-tabs" role="tablist">
    <li role="presentation"><a href="#" class="eqLogicAction" aria-controls="home" role="tab" data-toggle="tab" data-action="returnToThumbnailDisplay"><i class="fa fa-arrow-circle-left"></i></a></li>
    <li role="presentation" class="active"><a href="#eqlogictab" aria-controls="home" role="tab" data-toggle="tab"><i class="fa fa-tachometer"></i> {{Equipement}}</a></li>
    <li role="presentation"><a href="#commandtab" aria-controls="profile" role="tab" data-toggle="tab"><i class="fa fa-list-alt"></i> {{Commandes}}</a></li>
  </ul>
  <div class="tab-content" style="height:calc(100% - 50px);overflow:auto;overflow-x: hidden;">
    <div role="tabpanel" class="tab-pane active" id="eqlogictab">
      <br/>
      <div class="row">
        <div class="col-sm-6">
          <form class="form-horizontal">
            <fieldset>
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
                  <label class="checkbox-inline"><input type="checkbox" class="eqLogicAttr" data-l1key="isEnable" checked/>{{Activer}}</label>
                  <label class="checkbox-inline"><input type="checkbox" class="eqLogicAttr" data-l1key="isVisible" checked/>{{Visible}}</label>
                </div>
              </div>
              <div class="form-group">
                <label class="col-sm-3 control-label" >{{Objet parent}}</label>
                <div class="col-sm-4">
                  <select class="eqLogicAttr form-control" data-l1key="object_id">
                    <option value="">{{Aucun}}</option>
                    <?php
foreach (jeeObject::all() as $object) {
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
           <div class="form-group">
            <label class="col-sm-3 control-label"></label>
            <div class="col-sm-9">
              <label class="checkbox-inline"><input type="checkbox" class="eqLogicAttr" data-l1key="configuration" data-l2key="noBatterieCheck"/>{{Ne pas verifier la batterie}}</label>
            </div>
          </div>
          <div class="form-group">
            <label class="col-sm-3 control-label">{{Délai maximum autorisé entre 2 messages (min)}}</label>
            <div class="col-sm-4">
              <input class="eqLogicAttr form-control" data-l1key="timeout" />
            </div>
          </div>
        </fieldset>
      </form>
    </div>
    <div class="col-sm-6">
      <form class="form-horizontal">
        <fieldset>
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
   <div class="form-group">
    <label class="col-sm-3 control-label">{{Création}}</label>
    <div class="col-sm-3">
      <span class="eqLogicAttr label label-default" data-l1key="configuration" data-l2key="createtime" style="font-size : 1em;cursor : default;"></span>
    </div>
    <label class="col-sm-3 control-label">{{Statut}}</label>
    <div class="col-sm-2">
      <span class="eqLogicAttr label label-default" data-l1key="status" data-l2key="state" style="font-size : 1em;cursor : default;"></span>
    </div>
  </div>
  <div class="form-group">
    <label class="col-sm-3 control-label hasCommunication">{{Communication}}</label>
    <div class="col-sm-3 hasCommunication">
      <span class="eqLogicAttr label label-default" data-l1key="status" data-l2key="lastCommunication" style="font-size : 1em;cursor : default;"></span>
    </div>
    <label class="col-sm-3 control-label hasBatterie">{{Batterie}}</label>
    <div class="col-sm-3 hasBatterie">
      <span class="eqLogicAttr label label-default" data-l1key="status" data-l2key="battery" style="font-size : 1em;cursor : default;"></span> %
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
  <img src="core/img/no_image.gif" data-original=".jpg" id="img_device" class="img-responsive" style="max-height : 250px;" onerror="this.src='plugins/edisio/plugin_info/edisio_icon.png'"/>
</center>
</fieldset>
</form>
</div>
</div>
</div>
<div role="tabpanel" class="tab-pane" id="commandtab">
  <a class="btn btn-success btn-sm cmdAction pull-right" data-action="add" style="margin-top:5px;"><i class="fa fa-plus-circle"></i> {{Ajouter une commande}}</a><br/><br/>
  <table id="table_cmd" class="table table-bordered table-condensed">
    <thead>
      <tr>
        <th style="width: 300px;">{{Nom}}</th>
        <th style="width: 130px;">{{Type}}</th>
        <th>{{Logical ID (info) ou Commande brute (action)}}</th>
        <th>{{Paramètres}}</th>
        <th style="width: 100px;">{{Options}}</th>
        <th></th>
      </tr>
    </thead>
    <tbody>

    </tbody>
  </table>

</div>
</div>

</div>
</div>

<?php include_file('desktop', 'edisio', 'js', 'edisio');?>
<?php include_file('core', 'plugin.template', 'js');?>
