# Andamento, dúvidas, ideias e reflexões

## Capítulo teórico

Este é o tóptico que menos avancei em termos de teorias (heterodoxas) de crescimento. Minha maior preocupação deste capítulo é fazer mais do mesmo. No entanto, como havia me dito, tenho consciência que este capítulo será o menos inédito da minha dissertação mas é importante para dar o embasamento dos demais. Além disso, dada a minha estrutura de três ensaios, estou pensando em alguma questão à ser aprofundada neste capítulo de tal forma que se sustente por si só e, ao mesmo tempo, não seja desconexo em relação aos demais.

Em um primeiro momento, tenho pensando em dar mais atenção aos debates envolvendo distribuição de renda e conectar com as teorias do crescimento. Na dissertação que me passou no último e-mail, a autora fazia o caminho inverso que, por sinal, era o caminho que eu tinha em mente. 

Por fim, gostaria de dizer que as últumas leituras que tenho feito envolvem muito mais um apanhado das teorias da distribuição do que das teorias do crescimento. Sendo assim, estava pensando em aprofundar a teoria do Piveti neste capítulo (plano inicial era utilzar no próximo) e fazer as devidas pontes e contrapontos com as demais teorias. 

## Capítulo descritivo (Brasil)

Tenho percebido uma efervecência no debate em torno da concentração e desigualdade de renda e riqueza após a publicação do livro do Piketty e notei o mesmo para o caso brasileiro. Muitos *working papers* paracem estar preocupados em analisar a "hipótese Piketty" à luz dos novos dados divulgados do IRPF. Os debates que envolvem políticas redistrivutivas, por sua vez, se concentram muita mais em uma discussão do mercado de trabalho e seus impactos macroeconômicos. No entanto, me parece que esses dois caminhos não estão chegando à conclusões congruentes. De um lado, os autores que analisam os dados do IRPF concluem que a melhora da distrimuição de renda é menor do que imaginávamos/gostaríamos. Os demais, especialmente a Laura Carvalho e o Fernando Rugitsky, dizem que a melhora na distribuição é sem precendetes (talvez eu esteja exagerando um pouco) e, muito curiosamente, rumam para uma discussão envolvendo investimento público para aumentar nossa produtividade (Instituto das Garças não poderia estar mais entusiasmado...)

Eu, no entanto, estou mais em linha com o último artigo do Serrano e Freitas junto com as leituras do "cidadão consumidor". Meu maior receio é fazer o mesmo do que esses autores já fizeram, mas me parecen o caminho mais razoável e lógico. Ouvi dizer que um artigo escrito pelo Fagnani e Pedro Rossi (?) vão por esse caminho também. Teria mais textos para me indicar à respeito?

Em relação à crédito e endividamento das famílias para o caso brasileiro, avancei muito pouco na leitura. Para ser sincero, li os abstracts de alguns artigos e teses. Tenho notado que a discussão envolvendo crédito vai muito para o lado do crédito consignado enquanto os textos envolvendo endividamento das famílias são mais de instituições financeiras e documentos do IPEA. Recentemente encontrei uma monografia de um aluno da UFRJ que discutiu sustentabilidade desse ciclo expansimo de crédito, mas não fui muito além disso.

Por fim, dei uma reduzaida em relação aos dados. No moemnto, vou seguir seu conselho e notar algumas variáveis que são relavantes na literatura. Penso nisso não apenas para ter elementos para estruturar minha pesquisa, mas também para não argumentar sozinho e ficar distante do debate corrente. Isso não impediu, porém, de estar procurando alguns dados por mera curiosidade e me parece que existem alguns elementos que podem me ser úteis. Para dar um exemplo, tive a curiosidade de plotar alguns gráficos no R e, com isso, podem surgir informações relavantes (não necessariamente em termos da dissertação).



## Capítulo analítico (modelo)

Segue o que entendo por supermultiplicador (sem formalização):

- Para uma dada propensão marginal à poupar, os gastos improdutivos permitem que a propensão média à poupar se ajuste à propensão marginal à investir de tal modo que a utilização da capacidade produtiva corvirja para o nível normal
- O mecanismo que permite essa convergência é a concorrência capitalista assim como a estabilidade do sistema depende que a propensão marginal à invertir não seja muito elevada

Uma impressão que tive é que a existência de gastos autônomos em si legitimam o mecanismo iniciado pelo super. O fato deles serem ou não autônomos dizem respeito ao que pode criar o crescimento econômico no longo prazo. Digo isso pelas discussões na literatura de tentar mostrar que o que o Serrano (1995) chama de gastos autônomos não são, no limite, autônomos de fato. 

Além disso, tenho notado tando a importância quanto o avanço de uma teoria em que o nível de utilização da capacidade converge para o nível normal. Em termos de HPE, isso parece resolver uma questão antiga deixada por Harrold e só parcialmente resolvida pelos modelos neo-kaleckianos (salvo as recentes readaptações desses modelos com o SSM)

- **MEMO:** Me lembro de ter lido no capítulo 8 do Lavoie (aula da Carol Baltar) o entusiasmo dele de restuarar o paradoxo da poupança e dos custos e mesmo assim preservar o fechamento do modelo Kaleckiano. Essa me parece uma questão muito cara para os neo-Kaleckianos, mas neste capítulo em questão me soou um pouco ad hoc. Achei melhor não levantar esta questão em aula.

Com isso, tenho percebido o seguinte na literatura:

- Alguns autores argumentam que o modelo do super (SSM) se tornaria mais completo se endogeneizasse a capacidade de utilização normal
  - **Minhas impressões:** É uma leitura enganosa do SSM por dois motivos: (i) trata o mecanismo de ajuste rumo ao nível de utilização normal como estático e (ii) encaram o nível como exógeno e imutável sendo que o modelo do SSM afirma que o nível de utilização da capacidade produtiva converge ao normal **junto** do ajuste do investimo para atender mudanças na demanda efetiva de longo prazo
    - Sem contar que dizer que o nível normal de utilização da capacidade é exógeno contradiz o que o próprio Serrano (1995) diz (fora outros artigos)
- Outros autores afirmam que o crescimento é *supply-led*
  - **Minhas impressões:** Dizer que o investimento é induzido não é o mesmo que dizer que o crescimento é restringido ou guiado pela oferta. Além disso, me parece o modelo que mais levou o princípio da demanda efetiva às suas últimas consequência (no LP)
- Há um grande esforço na literatura PK de incluir as conclusões do SSM
  - Há uma frente que tenta restaurar e revitalizar as conclusões dos modelos neo-kaleckianos
  - Tentativas de endogeinização dos gastos autônomos
  - Outrs autores indicam que muito do que não é preciso recorrer ao modelo do SSM para o curto prazo uma vez que os modelos PK tradicionais (i.e. neo-kaleckianos) chegam ao mesmo resultado
  - Uma das formas que vem sido feita tem sido via SFC
    - Tentativa tanto de endogeinizar o Z quanto a distribuição de renda
    - Aprimoramento de uma estrutura financeira mais complexa

Em relação ao super imagino que tenho muito o que estudar ainda. No entanto, a compreensão e utilização total do modelo, creio eu, será possível apenas com o avanço da pesquisa. Sendo assim, me concentrarei nas questões que foram e que podem ser tratadas utilizando este modelo. À princípio, imagino que estudar a relação entre consumo-crédito e endividamento privado sejam o mais interessanrte, mas não sei até que ponto isso é possível ou diferente do que já foi feito (vide artigo do Gabriel).

Sobre a simulação, tenho noção de que não será (nada) fácil ainda mais por se tratar da economia brasileira. Além disso, não tenho pretenções (e sei que mesmo se tivesse seria impossível) de simular a economia brasileira como um todo, mas sim de algum componente relevante que minha investigação trouxer.  Neste caso, minha ideia aponta para um certo grau de qualificação ao "sraffiano" do super, ou seja, como se fosse um supermultiplicador da teoria monetária da distribuição.

### Dúvidas

- O modelo do SSM se tornaria instável se a propensão marginal à poupar fosse endogeneizada?
- Adotar o SSM implica em rejeitar a relação (ao menos direta) entre acumulação e distribuição? A inversa é válida?
  - Digo isso porque naquele artigo que me passou sobre os programas de pesquisa Sraffianos, o autor apresenta duas alternativa exclutendes para distribuição de renda: equação de cambridge (versão Sraffiana) e aboradagem do Piveti. Pretendo seguir a teoria monetária da distribuição e, com isso, me parece que estou, por exclusão, rejeitando a abordagem da acumulação
    - Pelo que entendi, partindo da teoria sraffiana, existe apenas um grau de liberdade na determinação da distribuição. Dessa forma, me parece que adatando a abordagem do Piveti eu estaria esgotando todos os graus de liberdade disponíveis
    - **OBS:** Não tenho pretenções de seguir a abordagem da acumulação, só queria saber das consequências teóricas dentro das linhas de pesquisa sraffianas para não incorrer em nenhuma incongruência 
