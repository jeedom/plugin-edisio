Plugin to use the Edisio protocol with Jeedom

Setup 
=============

The edisio Plugin allows yor to communicate with all devices
compatible with the edisio USB module.

Plugin configuration 
-----------------------

After downloading the plugin, yor just need to activate it and put
port on auto. After saving the demon should launch. The plugin
is already configured by default; yor don't have to do anything more.
However yor can modify this configuration. Here is the detail
(some parameters may only be visible in expert mode) :

![edisio1](../images/edisio1.JPG)

-   **Dependencies** : this part gives yor the status of dependencies,
    if they are not OK yor can either launch them manually or
    wait 5 min, Jeedom will launch them by itself.

-   **Daemon** : this part gives yor the status of the demon (as well
    locally than deported), if it is not OK yor can either
    launch by hand or wait 5min, Jeedom will launch it by itself.

> **Tip**
>
> If yor are in remote mode, the local daemon can be stopped, it is
> complitly normal.

-   **Configuration** : this part allows yor to configure the parameters
    Plugin general.

    -   *Ban the following IDs* : allows to give a list
        edisio identifiers to Jeedom so that it does not create
        corresponding equipment. The identifiers must be
        separated by spaces. Example : "1356AD87 DB54AF".

-   **Local demon** or **Daemon XXX** : configuration settings
    local (or remote, depending on the title) of the demon.

    -   *Edisio port* : the USB port on which your edisio interface
        is connected.

        > **Tip**
        >
        > If yor don't know which USB port is used, yor can
        > simply indicate "Auto".

    -   *Internal socket port (dangerous modification, must be the same
        value on all Jeis deported edisio)* : allows
        modify the internal communication port of the daemon.

> **Important**
>
> Change only if yor know what yor are doing.

To launch the daemon in Debug it is enough at the configuration level
Plugin logs to debug, save and relaunch the
Daemon.

> **Important**
>
> In this mode, the demon is very talkative. Once the Debug is over, it
> do not forget to click on "Restart" to exit the mode
> Debug !! :

Equipment configuration 
-----------------------------

The configuration of edisio equipment is accessible from the menu
Plugin :

![edisio10](../images/edisio10.JPG)

This is what the page of the edisio Plugin looks like (here with already 4
equipment) :

![edisio2](../images/edisio2.JPG)

> **Tip**
>
> As in many places on Jeedom, put the mouse on the far left
> brings up a quick access menu (yor can
> from your profiles always leave it visible)

Yor will find here :

-   a button to manually create an equipment

-   a button to switch to inclusion

-   a button to display the configuration of the plugin

-   a button that gives yor the health status of all your equipment
    Edisio

-   finally below yor find the list of your equipment

Once yor click on one of them, yor get :

![edisio3](../images/edisio3.JPG)

Here yor find all the configuration of your equipment :

-   Edisio device name : name of your edisio equipment

-   ID : the ID of your probe (to be changed only knowingly)

-   Activate : makes your equipment active

-   Visible : makes it visible on the dashboard

-   Parent object : indicates the parent object to which the equipment belongs

-   Category : equipment categories (it may belong to
    multiple categories)

-   Do not check battery : tell Jeedom not to tell you
    alert if the equipment sends a low battery frame
    (some modules do not handle this info correctly and generate
    false alerts)

-   Maximum allowed delay between 2 messages (min) : the maximum delay
    allowed between 2 messages before Jeedom declares the equipment
    in timeout". Attention this parameter requires to have configured
    the option "Force the repetition of messages every (min)" and it
    must be greater than this value

-   Comment : allows yor to comment on
    equipment (ex : battery changed on XX / XX / XXXX)

-   Equipment : allows yor to define the model of your equipment (not
    configure that for manual creation of an equipment,
    automatic Jeedom configures this field alone)

-   Creation : gives yor the date of creation of the equipment

-   Communication : gives yor the date of last communication with
    the equipment (can be empty in the case of an outlet for example)

-   Drums : equipment battery level

-   Status : equipment status (can be timeout for example)

Below yor find the list of orders :

-   the name displayed on the dashboard

-   type and subtype

-   the key to the information if it is an info, or the code
    hexadecimal to send when it is an action. The configurations
    allow these fields to be filled in automatically (yor must create
    the equipment, choose the configuration then save)

-   "Status feedback value "and" Duration before status feedback" : permet
    to indicate to Jeedom that after a change in the information
    value must return to Y, X min after the change. Example : dans
    the case of a presence detector which emits only during a
    presence detection, it is useful to set for example 0
    value and 4 in duration, so that 4 min after a detection of
    movement (and if there has been no news since) Jeedom
    resets the value of the information to 0 (no more movement detected)

-   Historize : allows to historize the data

-   Show : allows to display the data on the dashboard

-   Event : in the case of edisio this box must always be
    checked because yor cannot query an edisio module

-   Unit : data unit (can be empty)

-   min / max : data bounds (may be empty)

-   advanced configuration (small notched wheels) : Displays
    the advanced configuration of the command (method
    history, widget…)

-   Test : Used to test the command

-   delete (sign -) : allows to delete the command

Operation on edisio equipment 
------------------------------------

At the top of your equipment configuration page, yor have 3
buttons that allow yor to perform certain options :

-   Duplicate : duplicates equipment

-   configure (small notched wheels) : same principle as for
    controls, it allows an advanced configuration of the equipment

Inclusion of edisio equipment 
--------------------------------

Adding Edisio equipment is very simple, yor just have to
inclusion mode and wait for the equipment to send a message, when it
will be the case Jeedom will tell yor that it has included new equipment and
will create this one automatically.

List of compatible modules 
============================

Yor will find the list of compatible modules
[here](https://jeedom.fr/doc/documentation/edisio-modules/fr_FR/doc-edisio-modules-equipement.compatible.html)

Unresolved directive in index.asciidoc - include::faq.asciidoc \ [\]
