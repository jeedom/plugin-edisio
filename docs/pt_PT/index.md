Plugin para usar o protocolo Edisio com o Jeedom

Configuração 
=============

O plugin edisio permite que você se comunique com todos os dispositivos
compatível com o módulo USB edisio.

Configuração do plugin 
-----------------------

Depois de baixar o plugin, basta ativá-lo e colocar
vestindo no automóvel. Depois de salvar o demônio deve lançar. O plugin
já está configurado por padrão; você não precisa fazer mais nada.
No entanto, você pode modificar esta configuração. Aqui está o detalhe
(alguns parâmetros podem estar visíveis apenas no modo especialista) :

![edisio1](../images/edisio1.JPG)

-   **Dependências** : esta parte fornece o status de dependências,
    se não estiverem bem, você pode iniciá-los manualmente ou
    espere 5 minutos, Jeedom irá lançá-los por si só.

-   **Demônio** : esta parte fornece o status do demônio (também
    localmente do que deportado), se não estiver OK, você pode
    iniciar manualmente onde esperar 5 minutos, o Jeedom o iniciará sozinho.

> **Tip**
>
> Se você estiver no modo remoto, o daemon local pode ser parado, é
> completamente normal.

-   **Configuration** : esta parte permite que você configure os parâmetros
    plugin geral.

    -   *Proibir os seguintes IDs* : permite dar uma lista
        identificadores edisio para Jeedom para que ele não crie
        equipamento correspondente. Os identificadores devem ser
        separados por espaços. Exemplo : "1356AD87 DB54AF".

-   **Demônio local** onde **Demônio XXX** : definições de configuração
    local (onde remoto, dependendo do título) do demônio.

    -   *Porto EDISIO* : a porta USB na qual sua interface edisio
        está conectado.

        > **Tip**
        >
        > Se você não souber qual porta USB é usada, poderá
        > basta indicar "Auto".

    -   *Porta de soquete interna (modificação perigosa, deve ser a mesma
        valor em todo o Edisio deportado Jeis)* : deixa
        modificar a porta de comunicação interna do daemon.

> **Important**
>
> Mude apenas se você souber o que está fazendo.

Para iniciar o daemon em depuração, é suficiente no nível de configuração
logs de plug-in para depurar, salvar e reiniciar o
Demônio.

> **Important**
>
> Nesse modo, o demônio é muito falador. Depois que a depuração termina, é
> não se esqueça de clicar em "Reiniciar" para sair do modo
> Depurar !! :

Configuração do equipamento 
-----------------------------

A configuração do equipamento edisio pode ser acessada no menu
plugin :

![edisio10](../images/edisio10.JPG)

É assim que a página do plugin edisio se parece (aqui com 4
equipamento) :

![edisio2](../images/edisio2.JPG)

> **Tip**
>
> Como em muitos lugares em Jeedom, coloque o mouse na extremidade esquerda
> abre um menu de acesso rápido (você pode
> dos seus perfis sempre o deixe visível)

Você encontra aqui :

-   um botão para criar equipamento manualmente

-   um botão para mudar para inclusão

-   um botão para exibir a configuração do plug-in

-   um botão que fornece o status de saúde de todos os seus equipamentos
    Edisio

-   finalmente abaixo você encontra a lista do seu equipamento

Depois de clicar em um deles, você obtém :

![edisio3](../images/edisio3.JPG)

Aqui você encontra toda a configuração do seu equipamento :

-   Nome equipamentos EDISIO : nome do seu equipamento edisio

-   ID : o ID do seu probe (a ser alterado apenas conscientemente)

-   Ativar : torna seu equipamento ativo

-   Visivél : torna visível no painel

-   Objeto pai : indica o objeto pai ao qual o equipamento pertence

-   Categoria : categorias de equipamentos (pode pertencer a
    várias categorias)

-   Não verificar a bateria : diga a Jeedom para não lhe contar
    alerta se o equipamento envia um quadro de bateria fraca
    (alguns módulos não lidam com essas informações corretamente e geram
    alertas falsos)

-   Tempo máximo permitido entre 2 mensagens (min) : o atraso máximo
    permitido entre 2 mensagens antes que a Jeedom declare o equipamento
    em timeout". Atenção, este parâmetro requer que você tenha configurado
    a opção "Forçar a repetição de mensagens a cada (min)" e
    deve ser maior que esse valor

-   COMMENTAIRE : permite que você comente
    equipamento (ex : bateria trocada em XX / XX / XXXX)

-   Equipamento : permite definir o modelo do seu equipamento (não
    configure isso para a criação manual de um equipamento,
    Jeedom automático configura esse campo sozinho)

-   Criação : fornece a data de criação do equipamento

-   Comunicação : fornece a data da última comunicação com
    o equipamento (pode estar vazio no caso de uma tomada, por exemplo)

-   Bateria : nível de bateria do equipamento

-   Estado : status do equipamento (pode ser o tempo limite, por exemplo)

Abaixo você encontra a lista de pedidos :

-   o nome exibido no painel

-   tipo e subtipo

-   a chave da informação, se é uma informação, onde o código
    hexadecimal para enviar quando é uma ação. As configurações
    permitir que esses campos sejam preenchidos automaticamente (você deve criar
    equipamento, escolha a configuração e salve)

-   "Valor do feedback do status "e" Duração antes do feedback do status" : permet
    para indicar a Jeedom que após uma alteração nas informações
    O valor deve retornar para Y, X min após a alteração. Exemplo : dans
    no caso de um detector de presença que emite apenas durante um
    detecção de presença, é útil definir, por exemplo, 0
    valor e 4 de duração, de modo que 4 minutos após a detecção de
    movimento (e se não houver notícias desde então) Jeedom
    redefine o valor da informação para 0 (não é mais detectado movimento)

-   Historicizar : permite historiar os dados

-   Display : permite exibir os dados no painel

-   Evento : no caso de edisio esta caixa deve ser sempre
    marcado porque você não pode consultar um módulo edisio

-   Unidade : unidade de dados (pode estar vazia)

-   min / max : limites de dados (podem estar vazios)

-   configuração avançada (pequenas rodas dentadas) : permite exibir
    a configuração avançada do comando (método
    história, widget ...)

-   Teste : permite testar o comando

-   excluir (assinar -) : permite excluir o comando

Operação em equipamentos Edisio 
------------------------------------

Na parte superior da página de configuração do seu equipamento, você tem 3
botões que permitem executar determinadas opções :

-   Duplicar : equipamento duplicado

-   configure (pequenas rodas dentadas) : mesmo princípio que para
    controles, permite uma configuração avançada do equipamento

Inclusão de equipamentos edisio 
--------------------------------

A adição de equipamentos Edisio é muito simples, basta você
modo de inclusão e aguarde o equipamento enviar uma mensagem, quando
será o caso da Jeedom lhe dizer que incluiu novos equipamentos e
criará este automaticamente.

Lista de módulos compatíveis 
============================

Você encontrará a lista de módulos compatíveis
[aqui](https://jeedom.fr/doc/documentation/edisio-modules/fr_FR/doc-edisio-modules-equipement.compatible.html)

Diretiva não resolvida no índice.asciidoc - incluir::faq.asciidoc \ [\]
