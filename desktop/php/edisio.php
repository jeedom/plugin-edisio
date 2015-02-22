<?php
if (!isConnect('admin')) {
    throw new Exception('Error 401 Unauthorized');
}
sendVarToJS('eqType', 'edisio');
$eqLogics = eqLogic::byType('edisio');
?>

<div class="row row-overflow">
    <div class="col-lg-2 col-md-3 col-sm-4">
        <div class="bs-sidebar">
            <ul id="ul_eqLogic" class="nav nav-list bs-sidenav">
                <center style="margin-bottom: 5px;">
                    <a class="btn btn-default btn-sm tooltips" id="bt_getFromMarket" title="{{Récupérer du market}}" style="display: inline-block;"><i class="fa fa-shopping-cart"></i> <span class="expertModeHidden">{{Market}}</span></a>
                </center>
                <a class="btn btn-default eqLogicAction" style="width : 100%;margin-top : 5px;margin-bottom: 5px;" data-action="add"><i class="fa fa-plus-circle"></i> {{Ajouter}}</a>
                <li class="filter" style="margin-bottom: 5px;"><input class="filter form-control input-sm" placeholder="Rechercher" style="width: 100%"/></li>
                <?php
                foreach ($eqLogics as $eqLogic) {
                    echo '<li class="cursor li_eqLogic" data-eqLogic_id="' . $eqLogic->getId() . '"><a>' . $eqLogic->getHumanName(true) . '</a></li>';
                }
                ?>
            </ul>
        </div>
    </div>

    <div class="col-lg-10 col-md-9 col-sm-8 eqLogicThumbnailDisplay" style="border-left: solid 1px #EEE; padding-left: 25px;">
        <legend>{{Mes équipement EDISIO}}
        </legend>
        <?php
        if (count($eqLogics) == 0) {
            echo "<br/><br/><br/><center><span style='color:#767676;font-size:1.2em;font-weight: bold;'>{{Vous n'avez pas encore d'équipement EDISIO, cliquez sur Ajouter pour commencer}}</span></center>";
        } else {
            ?>
            <div class="eqLogicThumbnailContainer">
                <?php
                foreach ($eqLogics as $eqLogic) {
                    echo '<div class="eqLogicDisplayCard cursor" data-eqLogic_id="' . $eqLogic->getId() . '" style="background-color : #ffffff; height : 200px;margin-bottom : 10px;padding : 5px;border-radius: 2px;width : 160px;margin-left : 10px;" >';
                    echo "<center>";
                    $urlPath = config::byKey('market::address') . '/market/edisio/images/' . $eqLogic->getConfiguration('device') . '.jpg';
                    $urlPath2 = config::byKey('market::address') . '/market/edisio/images/' . $eqLogic->getConfiguration('device') . '_icon.png';
                    $urlPath3 = config::byKey('market::address') . '/market/edisio/images/' . $eqLogic->getConfiguration('device') . '_icon.jpg';
                    echo '<img class="lazy" src="plugins/edisio/doc/images/edisio_icon.png" data-original3="' . $urlPath3 . '" data-original2="' . $urlPath2 . '" data-original="' . $urlPath . '" height="105" width="95" />';
                    echo "</center>";
                    echo '<span style="font-size : 1.1em;position:relative; top : 15px;word-break: break-all;white-space: pre-wrap;word-wrap: break-word;"><center>' . $eqLogic->getHumanName(true, true) . '</center></span>';
                    echo '</div>';
                }
                ?>
            </div>
            <?php } ?>
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
                                <label class="col-sm-3 control-label">Nom de l'équipement EDISIO</label>
                                <div class="col-sm-4">
                                    <input type="text" class="eqLogicAttr form-control" data-l1key="id" style="display : none;" />
                                    <input type="text" class="eqLogicAttr form-control" data-l1key="name" placeholder="Nom de l'équipement EDISIO"/>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-3 control-label">ID</label>
                                <div class="col-sm-4">
                                    <input type="text" class="eqLogicAttr form-control" data-l1key="logicalId" placeholder="Logical ID"/>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-3 control-label"></label>
                                <div class="col-sm-1">
                                    <label class="checkbox-inline">
                                        <input type="checkbox" class="eqLogicAttr" data-l1key="isEnable" checked/> Activer 
                                    </label>
                                </div>
                                <label class="col-sm-1 control-label"></label>
                                <div class="col-sm-1">
                                    <label class="checkbox-inline">
                                        <input type="checkbox" class="eqLogicAttr" data-l1key="isVisible" checked/> Visible 
                                    </label>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-3 control-label" >Objet parent</label>
                                <div class="col-sm-4">
                                    <select class="eqLogicAttr form-control" data-l1key="object_id">
                                        <option value="">Aucun</option>
                                        <?php
                                        foreach (object::all() as $object) {
                                            echo '<option value="' . $object->getId() . '">' . $object->getName() . '</option>';
                                        }
                                        ?>
                                    </select>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-3 control-label">Catégorie</label>
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
                                    <input type="checkbox" class="eqLogicAttr" data-l1key="configuration" data-l2key="noBatterieCheck"/>
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
                            <legend>Informations</legend>
                            <div class="form-group expertModeVisible">
                                <label class="col-sm-3 control-label">{{Date de création}}</label>
                                <div class="col-sm-5">
                                    <span class="eqLogicAttr label label-primary" data-l1key="configuration" data-l2key="createtime"></span>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="col-sm-3 control-label">Equipement</label>
                                <div class="col-sm-6">
                                 <select class="eqLogicAttr form-control" data-l1key="configuration" data-l2key="device">
                                    <option value="">Aucun</option>
                                    <?php
                                    foreach (edisio::devicesParameters() as $mid => $info) {
                                        echo '<option value="' . $mid . '">' . $info['name'] . '</option>';
                                    }
                                    ?>
                                </select>
                            </div>
                            <div class="col-sm-3">
                                <a class="btn btn-warning" id="bt_shareOnMarket"><i class="fa fa-cloud-upload"></i> {{Partager}}</a>
                            </div>
                        </div>
                        <div class="form-group expertModeVisible">
                            <label class="col-sm-3 control-label">{{Envoyer une configuration}}</label>
                            <div class="col-sm-5">
                                <input id="bt_uploadConfEnocean" type="file" name="file" data-url="plugins/enocean/core/ajax/edisio.ajax.php?action=uploadConfEdisio">
                            </div>
                        </div>
                        <div class="form-group expertModeVisible">
                            <label class="col-sm-3 control-label">{{Délai maximum autorisé entre 2 messages (min)}}</label>
                            <div class="col-sm-4">
                                <input class="eqLogicAttr form-control" data-l1key="timeout" />
                            </div>
                        </div>
                    </fieldset> 
                </form>
            </div>
        </div>

        <legend>Commandes</legend>


        <a class="btn btn-success btn-sm cmdAction" data-action="add"><i class="fa fa-plus-circle"></i> Ajouter une commande</a><br/><br/>
        <table id="table_cmd" class="table table-bordered table-condensed">
            <thead>
                <tr>
                    <th style="width: 300px;">Nom</th>
                    <th style="width: 130px;" class="expertModeVisible">Type</th>
                    <th class="expertModeVisible">Logical ID (info) ou Commande brute (action)</th>
                    <th >Paramètres</th>
                    <th style="width: 100px;">Options</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>

            </tbody>
        </table>

        <form class="form-horizontal">
            <fieldset>
                <div class="form-actions">
                    <a class="btn btn-danger eqLogicAction" data-action="remove"><i class="fa fa-minus-circle"></i> Supprimer</a>
                    <a class="btn btn-success eqLogicAction" data-action="save"><i class="fa fa-check-circle"></i> Sauvegarder</a>
                </div>
            </fieldset>
        </form>

    </div>
</div>

<?php include_file('desktop', 'edisio', 'js', 'edisio'); ?>
<?php include_file('core', 'plugin.template', 'js'); ?>
