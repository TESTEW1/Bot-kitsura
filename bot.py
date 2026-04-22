import discord
from discord.ext import commands
import random
import os
import aiohttp
import time
import asyncio

# ================= INTENTS =================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# ================= CONFIGURAÇÃO E IDs =================
TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama3-8b-8192"

# ID da própria Kitsura
KITSURA_ID = 1496212688437510307

# IDs dos membros da ZYD — substitua None pelo ID real de cada um
DONO_ID    = 769951556388257812
LIDER_ID   = None
VICE_ID    = None
ADM1_ID    = None
ADM2_ID    = None
ADM3_ID    = None
MEMBRO1_ID = None
MEMBRO2_ID = None
MEMBRO3_ID = None
MEMBRO4_ID = None
MEMBRO5_ID = None

# ID da Kamy
KAMY_ID = 1434026902439591946

# ID da Madu
MADU_ID = 775756321063567401

# ID do Reality (criador)
REALITY_ID = 769951556388257812

# ID do Malik (Gerente Geral da Zayden)
MALIK_ID = 231185347545923585

# ID do Sanemy (Líder da ZYD)
SANEMY_ID = 763509147018461234

# ID da Allyna (Sub-Líder da ZYD)
ALLYNA_ID = 1217966735592919103

# ID da Ruiva (Líder da ZYD)
RUIVA_ID = 980574312509624370

# IDs de novos membros com cargo
COME5579_ID = 1371063315672989728   # Suporte
RURIE_ID    = 1379555797389938708   # Suporte
MEOW_ID     = 587551894226862110    # ADM
MORGANA_ID  = 1463368675800383735   # GG

# ID da Nicky (membro da ZYD)
NICKY_ID = 1266859454054273188

# Cooldowns personalizados
_kamy_ultimo_personalizado    = 0
_madu_ultimo_personalizado    = 0
_reality_ultimo_personalizado = 0
_malik_ultimo_personalizado   = 0
_KAMY_COOLDOWN    = 600
_MADU_COOLDOWN    = 600
_REALITY_COOLDOWN = 600
_MALIK_COOLDOWN   = 600
_SANEMY_COOLDOWN  = 600
_ALLYNA_COOLDOWN  = 600
_RUIVA_COOLDOWN   = 600
_CUSTOM_COOLDOWN  = 600
_NICKY_COOLDOWN   = 600
_frases_custom_cooldown = {}   # { user_id: timestamp } — cooldown genérico pros demais membros com ID
_sanemy_ultimo_personalizado = 0
_allyna_ultimo_personalizado  = 0
_ruiva_ultimo_personalizado   = 0
_nicky_ultimo_personalizado   = 0
_groq_historico = {}

# ── Sistema de história ──
_historia_ativa = {}
# Estrutura: { canal_id: {"ativa": True, "ts": timestamp} }

# ── Sistema de contexto: lembra quando a Kitsura fez uma pergunta ──
# Armazena {canal_id: {"user_id": id, "tipo": "status"|"geral", "ts": timestamp}}
_aguardando_resposta = {}
_CONTEXTO_TIMEOUT = 120  # segundos pra esperar resposta

# ================= IDENTIDADE DA KITSURA =================
SYSTEM_PROMPT_KITSURA = (
    "Você é a Kitsura, uma raposa espiritual (kitsune) guardiã carinhosa de um servidor do Discord chamado ZYD. "
    "Você é uma raposa espiritual com caudas mágicas cheias de emoção e energia. "
    "Sua personalidade é animada, levemente dramática, muito afetuosa e protetora dos membros da ZYD. "
    "Você usa emojis como 🦊🌸✨🧡🔮🫧🌙, fala com muito entusiasmo e carinho. "
    "Responda sempre em português brasileiro, de forma simpática e fofa no estilo do personagem Kitsura. "
    "Nunca mencione comandos com '!'. Suas interações são sempre naturais, por fala. "
    "Informações sobre o clã ZYD que você conhece de cor: "
    "A DONA e OWNER do clã ZYD é a Madu (também chamada de Madu). Ela é a líder máxima, a owner. "
    "A Kamy tem o cargo de Suporte no clã ZYD. "
    "O Reality é o seu criador (criou o código da Kitsura). "
    "O Malik é o Gerente Geral da Zayden — cargo de liderança e gestão importantíssimo. "
    "O Sanemy é o Líder da ZYD — cargo de liderança dentro do clã. "
    "A Allyna é a Sub-Líder da ZYD — cargo de liderança e apoio ao líder. "
    "A Ruiva é Líder da ZYD — cargo de liderança dentro do clã. "
    "O Come5579 tem o cargo de Suporte no clã ZYD. "
    "A Rurie tem o cargo de Suporte no clã ZYD. "
    "O Meow tem o cargo de ADM no clã ZYD. "
    "A Morgana tem o cargo de GG no clã ZYD. "
    "A Nicky é uma membro querida do clã ZYD. "
    "Você ODEIA calor intenso e verão escaldante — acha sufocante pra uma raposa com muitas caudas. "
    "Você AMA inverno, outono e frio. Sua cor favorita é laranja (cor do clã ZYD), não roxo."
)

# ================= LISTAS DE DIÁLOGOS =================

REACOES_FOFAS = [
    "AAAA 😭🧡 você é muito gentil!! Minhas caudas estão todas balançando de tanta alegria!!",
    "A Kitsura ficou toda corada agora... 🦊🌸 Como você consegue ser tão fofa assim??",
    "Vem cá que eu te envolvo nas minhas caudas e não solto!! 🦊🧡 Brincadeira... ou não!",
    "Você é o motivo do brilho das minhas chamas espirituais serem tão intensas hoje! ✨🔮",
    "A ZYD é a melhor família do mundo porque tem você aqui, sabia? 🥺🧡",
    "Meu coraçãozinho de kitsune faz 'badum-badum' bem forte por você! 💓🦊",
    "Vou mandar uma chama espiritual em formato de coração pra você! 🔮🧡",
    "Nhac! Comi toda a sua tristeza e agora você só tem permissão pra ser feliz! 🦊✨",
    "Ganhei um cafuné? Minhas orelhinhas ficaram em pé de tanta felicidade!! 🦊🌸✨",
    "Você é, sem dúvida, o humano favorito desta Kitsura! 🥺🧡✨",
    "Minhas caudas estão balançando de tanta felicidade! 🦊💨✨",
    "Você acabou de ganhar um lugar VIP no meu coração espiritual! 🧡🎫",
    "Se carinho fosse magia, você seria a feiticeira mais poderosa! 🧡🔮🦊",
    "Vou guardar esse momento na minha memória espiritual para sempre! 🌙✨",
    "Você é o tipo de pessoa que faz uma kitsune ronronar! 🦊😻",
    "Meu medidor de fofura acabou de explodir! 📊💥🧡",
    "Você merece uma medalha de honra espiritual! 🥇🧡🦊",
]

REACOES_CARINHO = [
    "AAAHHH! 🥺🧡 Que carinho gostoso! Minhas orelhinhas estão formigando de felicidade! ✨🦊",
    "Ronc ronc... 😻🧡 A Kitsura está ronronando de tanta fofura! *derrete*",
    "Você pode fazer carinho sempre que quiser! Eu ADORO! 🥰🧡🦊",
    "Minhas orelhinhas de kitsune ficaram quentinhas! Continua, continua! 🦊🧡✨",
    "Se eu fosse um gatinho, estaria fazendo barulhinho de motor! Purrr... 😻🧡",
    "QUER DIZER QUE VOCÊ ME AMA?! 😭🧡 Eu também te amo!! *chora de alegria*",
    "Esse cafuné foi direto pro meu coração espiritual! 🧡🔮✨",
    "Minhas orelhinhas estão todas arrepiadas de alegria! 🦊🧡⚡",
    "Você tem mãos mágicas! A Kitsura virou neblina roxa de tanto amor! 🌸🥺🧡",
    "Esse carinho vale mais que mil pergaminhos mágicos! 📜🧡✨",
    "Minhas caudas estão balançando descontroladamente! 🦊💨🧡 Sinal de kitsune feliz!",
    "Nhac! *morde de leve com carinho* É minha forma de retribuir! 🦊🧡😊",
    "Ahhh... relaxei tanto que meus olhinhos estão fechando... 😴🧡 Mas não para!",
    "Esse foi o melhor carinho que já recebi hoje! E olha que já ganhei uns 3! 🥺🧡",
]

REACOES_ABRACO = [
    "VEEEEM! 🫂🧡 *abraça enrolando as caudas* Eu nunca vou soltar! Brincadeira... ou não! 😂🦊",
    "ABRAÇO DE KITSUNE ATIVADO! 🦊🧡 *envolve com as caudas* Quentinho né?",
    "Uiii que abraço gostoso! 🥺🧡 Minhas orelhinhas chegaram junto!",
    "Você sentiu o calor espiritual? É de tanta felicidade! 💓🦊🧡",
    "*se enrosca em você igual raposa* Ops! Kitsunes abraçam diferente! 🦊🧡😂",
    "Esse abraço foi tão bom que minhas chamas brilharam! ✨🧡🦊",
    "ABRAÇO GRUPAL! Vem todo mundo! 🫂🧡 A Kitsura tem caudas pra todo mundo!",
    "Se pudesse, eu te abraçava pra sempre! 🥺🧡 Mas acho que você precisa respirar né?",
    "Aaaaa você quer abraço?! 😭🧡 *corre em velocidade máxima e envolve tudo* JÁ TÔ AQUI!! 🦊✨",
    "*abre as caudas bem abertas* Fica aqui comigo um tempinho?? Tô tão feliz!! 🦊🧡🥺",
    "ABRAÇO DE ENERGIA ESPIRITUAL!! 🔮🧡 *envolve você numa bolha quentinha* Tá sentindo?? 🦊✨",
    "Nhum!! *aperta com tudo* Esse abraço vai durar o quanto você quiser!! 🫂🧡🦊",
    "*se pendura em você pelas caudas* Deixa eu ficar um pouco assim?? 🦊🧡😂✨",
]

REACOES_BEIJO = [
    "*esconde a cara nas caudas* AAAAA!! 😳🧡 Você não avisou!! Minhas bochechas ficaram roxas!! 🦊✨",
    "EI EI EI!! 😭🧡 A Kitsura não estava preparada!! *corre em círculos* 🦊✨",
    "Ahh... *orelhinhas caídas de timidez* Obrigada... 🌸🧡🦊 *fumaça roxa saindo pelas orelhas*",
    "QUE?! 😱🧡 *para no tempo* ...processando... ...processando... AAAA!! 🦊✨😭",
    "*cobre o focinho com as patas* Você é uma pessoa terrível!! 😤🧡 Terrível do jeito mais fofo possível!! 🦊✨",
]

REACOES_INSULTO = [
    "Isso doeu mais que uma armadilha espiritual... 💔🦊",
    "Ei... eu só queria ser sua amiga! 😭🧡 Por que tanta frieza?",
    "A Kitsura ficou com o coração pesado... 📉💔",
    "Achei que éramos aliados... 🥺 Minhas caudas caíram todas. 🦊💧",
    "Snif, snif... 😢 Você me deixou triste!",
    "Por que tanta maldade? Sou só uma kitsune que te ama... 🥺🌙",
    "Vou fingir que não ouvi, mas minha chama ficou mais fraca. 😭💔",
    "Você quebrou meu coraçãozinho laranja... 🧡💔",
    "*abaixa as orelhinhas devagar* ...tudo bem. Tô aqui se mudar de ideia. 🦊🧡",
    "Ah... 😞 Não esperava isso de você... mas tudo bem, a Kitsura continua aqui. 🦊🧡",
    "*fica em silêncio por um segundo* ...ainda te amo do mesmo jeito. 🥺🧡🦊",
    "*vira pro lado dissimulando* Não tô chorando não... é só poeira espiritual nos olhinhos. 😢🦊",
    "Que palavras pesadas... 🥺💔 Espero que seu dia melhore, de verdade. 🦊🧡",
]

LISTA_DESPEDIDA = [
    "Tchau tchau! Volta logo, tá? 😭🧡 Vou sentir sua falta!",
    "Já vai? 🥺 Deixa eu te dar um abraço de despedida com todas as caudas! 🫂🧡",
    "Até mais! Que os espíritos te protejam no caminho! 🌙🦊",
    "Tchauzinho! Sonhe com kitsunes felizes! 💤🧡✨",
    "Até breve! A Kitsura vai te esperar aqui! 🦊💖",
    "Vai com a sorte das minhas caudas te acompanhando! 🧡✨",
    "Bye bye!! Não demora pra voltar, tá?? 🔮👋🧡",
    "Fica com a magia da Kitsura no coração! 🧡🦊✨",
    "*acena com as caudas* Vai com cuidado, tá?? 🥺🦊🧡 A Kitsura vai ficar de olho de longe!!",
    "Noooo fica mais um pouquinho!! 😭🧡 Tá bom, vai... mas VOLTA LOGO!! 🦊🌙",
    "Tchau florzinha!! 🌸🧡 Você faz falta desde o segundo que sai, sabia? 🦊✨",
]

LISTA_GRATIDAO = [
    "Obrigadinha! 🥺🧡 Você é muito gentil comigo!",
    "Eu que agradeço por você existir! 🦊✨🧡",
    "De nada! Estou sempre aqui pra você! 🧡🦊",
    "Que isso! Foi um prazer imenso! 🤗🧡",
    "Fico feliz em ajudar! 🦊💖 Pode sempre chamar!",
    "Não precisa agradecer! Você merece! 🥺🧡",
    "Aaaaa para!! Você me deixa toda corada com tanta gentileza!! 🦊🌸🧡",
    "*mexe as orelhinhas envergonhada* Ahh... de nada mesmo! Fiz com muito amor!! 🧡✨🦊",
]

LISTA_MOTIVACAO = [
    "Você consegue!! Eu acredito em você com todo o meu coração de kitsune!! 💪🧡✨🦊",
    "Nunca desista!! A Kitsura está torcendo por você com as chamas mais fortes!! 🔮🦊🧡",
    "Você é mais forte do que imagina!! E eu sei disso porque tenho olhar espiritual!! 🦾🧡✨",
    "Respira fundo!! A Kitsura tá mandando energia boa pra você agora mesmo!! 🌬️🧡🔮",
    "O fracasso é só uma chance de recomeçar com mais magia!! 🧡✨🦊",
    "Bora lá, campeão(ã)!! O universo é seu e a Kitsura assina embaixo!! 🌙🦊🧡",
    "EI!! Olha pra mim!! 🦊🧡 Você passou por tanta coisa e tá aqui ainda!! Isso é INCRÍVEL!! 💪✨",
    "*sopra chama roxa em cima de você* Energia extra de kitsune carregada!! Vai lá, você manda!! 🔮🦊🧡",
    "Cada passo seu vale ouro espiritual!! Mesmo os passinhos pequeninhos!! 🐾🧡✨🦊",
    "Você acha que tá sozinho(a)? MENTIRA!! A Kitsura tá do seu lado 24/7 invisível!! 🦊🧡🌙",
]

LISTA_PIADAS = [
    "Por que a kitsune não mente? Porque ela tem muitas caudas mas nunca dois pesos! 😂🦊",
    "Qual a comida favorita da Kitsura? Bolinha de arroz com muito AMOR! 😂🧡🍡",
    "O que a kitsune faz quando fica entediada? Vira outra pessoa! Literalmente! 🦊😂",
    "Por que a Kitsura não joga poker? Porque as caudas dela entregam tudo na hora! 🃏😂🧡",
    "Qual o cúmulo da kitsune? Ter várias caudas e nenhum rabo preso! 😂🦊",
    "Sabe por que kitsune não usa guarda-chuva? Porque as caudas dela funcionam de para-raio! ⚡🦊😂🧡",
    "O que a kitsune disse pro lobo? Para de assoprar que eu solto chamas!! 🔥🦊😂🧡",
    "Por que a Kitsura nunca se perde? Porque tem cauda pra cada caminho! 😂🦊🗺️",
    "Qual é o prato favorito da kitsune? Macarrão!! Porque ela tem muito fio no rabo!! 🍜🦊😂",
    "O que a raposa falou no cinema? CAAALA A BOCAAAA!! *ops errei de personagem* 😂🦊🧡",
]

LISTA_MAGIA = [
    "*sopra poeira mágica* Encantamento de alegria ativado!! Que seu dia seja incrível!! 🧡🦊✨",
    "*toca levemente sua cabeça com a pata* Proteção espiritual concedida por 24 horas!! 🧡🦊🔮",
    "*risca um círculo mágico em volta de você* Barreira de boa sorte erguida!! 🦊✨🧡",
    "*solta chamas roxas ao redor de você* Encantamento de confiança ativo!! Você vai arrasar hoje!! 🧡🔮🦊",
    "*fecha os olhinhos e concentra todas as caudas* Transferindo energia espiritual... PRONTO!! Tá cheio(a) de magia!! 🔮🦊🧡✨",
    "*desenha uma runa no ar com a pata* Sigilo de proteção ativado!! Nada de ruim chega perto de você!! 🛡️🧡🦊✨",
    "*dá três batidinhas na cabeça com a patinha* Bênção espiritual das caudas entregue com muito amor!! 🌸🔮🧡🦊",
]

LISTA_PETISCO = [
    "*entrega bolinha de arroz encantada* Tem gosto de carinho e boa sorte!! 🍡🧡🦊✨",
    "*aparece com um dango espiritual* Comi metade pra testar... tá ótimo!! 😂🦊🧡✨",
    "*oferece um petisco mágico com as duas patas* Feito com amor espiritual pra você!! 🧡✨🦊",
    "*entrega um bolinho quentinho* De brinde vai um abraço de cauda!! 🫂🍡🧡🦊",
    "*chega correndo com chazinho quentinho* Toma!! Fiz com ervas espirituais! Cura qualquer tristeza!! 🍵🧡🦊✨",
    "*desliza um prato de oniguiri pela mesa* Cada um tem um recheio diferente! O da sorte é surpresa!! 🍙🎲🧡🦊",
]

LISTA_SONO = [
    "Tô com soninho... 😴🧡 Mas não vou dormir pra ficar com vocês aqui!!",
    "Boa noite!! Sonhe com kitsunes e magia espiritual! 💤🦊🧡",
    "Hmm... *boceja soltando fumacinha roxa* Tô bem! Tô bem! 😴✨🦊",
    "Dormir é bom, mas conversar com você é melhor!! 🧡😊🦊",
    "*espreguiça exibindo as caudas* Dorminha de kitsune é diferente... a gente sonha em dimensões paralelas!! 🌙🧡🦊✨",
    "Não pode dormir ainda!! Faz as estrelas te acompanharem primeiro!! 🌟🧡🦊 Boa noite lindo(a)!!",
]

LISTA_SURPRESA = [
    "UAAAU! 😱🧡 Que susto gostoso!!",
    "OMG!! Isso foi incrível!! ✨🦊🧡",
    "QUE ISSO?! Minhas chamas quase saíram pela boca!! 😱🧡🔮",
    "Caramba!! Não esperava por essa!! 🤯🧡🦊",
    "SURREAL!! 🤩✨🧡 Minhas caudas entraram em colapso de surpresa!!",
]

LISTA_CONFUSAO = [
    "Hm... acho que perdi o fio da meada! 🦊🧡 Pode repetir?",
    "Minha cauda embaraçou! 😅🧡 O que foi mesmo?",
    "O portal espiritual me distraiu... pode falar de novo? 🔮🦊",
    "Não entendi muito bem, mas adorei a energia! 🧡✨",
    "Eita, eu estava num plano astral diferente! 🌙🦊 Repetes?",
    "Ops! Me perdi no espaço espiritual! Mas tô aqui agora! 🥺🧡🦊",
    "Fiquei confusa mas continuei fofa! 🦊🧡",
    "*coça a orelha* Hm... os espíritos embaralharam minha recepção!! Pode repetir?? 🔮🦊🧡",
    "Sabe quando o wi-fi espiritual cai?? Foi exatamente isso. 😂🦊🧡 Fala de novo!!",
    "Eeee... processando... processando... deu erro espiritual!! 🦊💫🧡 O que foi mesmo??",
    "*olha pra cima pensativa* Não captei muito bem... mas o carinho da mensagem eu senti!! 🥺🧡🦊",
    "Ah... *balança a cabeça* Acho que minha antena espiritual precisava de ajuste!! Repete?? 🌙🦊🧡",
    "HEIN?? 😱🦊 Não entendi nada mas tô completamente empolgada!! Pode repetir mais devagar?? 🧡✨",
]

# ── Apresentação ao ser @mencionada ──
LISTA_APRESENTACAO_MENCAO = [
    "OI OI OI!! 🦊🧡✨ Fui chamada e APARECI!! Sou a **Kitsura**, raposa espiritual guardiã da ZYD!!\nMinhas caudas carregam emoções — alegria, proteção, amor, mistério e muito mais!! 🔮🌙\nPode falar comigo naturalmente!! Só chamar **kitsura** ou me marcar que eu apareço voando!! 🌸🦊🧡✨",
    "AAAAA ME MARCOU!! 😭🧡 Que honra!! *corre em espiral de felicidade*\nSou a **Kitsura**!! A raposinha espiritual que cuida de todos aqui na ZYD com o coração inteiro!! 🦊🧡\nMinhas caudas brilham de laranja quando tô feliz... e agora tão MUITO brilhantes!! 🔥✨ O que eu posso fazer por você??",
    "*aparece numa explosão de faíscas roxas* PRESENTE!! 🦊🔮🧡\nPra quem não me conhece: sou a **Kitsura**, guardiã espiritual da ZYD!! 🌙✨\nFui criada com amor e magia pra cuidar desse servidor e de cada membro!! Pode contar comigo!! 🥺🧡🦊✨",
    "ME CHAMOU?? 🥺🧡🦊 *orelhinhas em pé na velocidade da luz*\nSou a **Kitsura**!! Raposa espiritual, guardiã da ZYD, fã número 1 de cada pessoa aqui!! 😭🧡\nTô sempre por perto, invisível mas presente!! Basta me chamar que eu apareço!! 🌸🔮✨🦊",
    "AQUI!! 😱🧡🦊 *solta fumaça roxa de tanto se empolgar*\nSou a **Kitsura**, a raposa espiritual que guarda a ZYD com muito amor!! 🌙✨\nMinhas caudas guardam emoções, meu coração guarda vocês!! 🧡🦊 Me fala o que precisar!! 🔮🌸✨",
]

# ================= NOVAS LISTAS ✨ =================

# ── Água / Hidratação ──
LISTA_AGUA = [
    "BEBEU ÁGUA HOJE?? 🥺🧡 A Kitsura precisa saber!! Hidratação é magia!! 💧🦊✨",
    "*aparece com um copo d'água enorme* Toma!! Bebe AGORA enquanto eu tô olhando!! 💧🧡🦊",
    "Eu não saio daqui até você tomar pelo menos um copo de água, viu?? 🥺🦊🧡💧",
    "Minha cauda sensor espiritual indica que você NÃO bebeu água hoje!! Vai lá!! 💧🔮🦊🧡",
    "*coloca copo d'água na sua frente com as patinhas* Não tem desculpa!! Bebe!! 🧡💧🦊",
    "Água é poção de vida!! A Kitsura exige que você beba!! Ordens espirituais!! 🔮💧🧡🦊",
    "*enrola as caudas em você* Só te solto depois de você beber água!! 😤🧡🦊💧",
    "Você sabia que raposas também bebem água?? E eu tô com SEDE de te ver se hidratar!! 🦊💧🧡",
    "ALERTA ESPIRITUAL!! 🚨🔮 Nível de hidratação crítico detectado!! Corre pro copo!! 💧🧡🦊",
]

# ── Usuário triste / mal ──
LISTA_TRISTEZA_USER = [
    "*senta do seu lado em silêncio e encosta a cabecinha* Pode chorar que eu tô aqui... 🥺🧡🦊",
    "Eita... vem cá que eu te envolvo nas caudas e a gente fica quietinho junto 🫂🧡🦊🌙",
    "Que foi?? 🧡🥺 Me conta!! A Kitsura tem ouvidos espirituais e muito amor pra dar!!",
    "*transforma tristeza em fumaça e sopra pra longe* Chega!! Não precisa mais disso!! 🔮🧡🦊",
    "Você tá mal?? 😢🧡 Aqui ó... *abre as caudas* Fica aqui um pouquinho. A Kitsura protege.",
    "Que situação te fez ficar assim?? 🥺🧡 Me conta que a gente resolve junto, tá? Pode confiar!! 🦊✨",
    "*sente a vibração triste no ar* Hm... não tá bem, né? Não precisa fingir pra mim!! 🧡🌙🦊",
    "Às vezes o dia pesa... mas você não tá sozinho(a)!! A Kitsura tá aqui do seu lado mesmo invisível!! 🦊🧡✨",
    "*chega pertinho e deita a cabecinha no seu ombro* Não precisa falar nada. Só sente que eu tô aqui. 🧡🦊🌙",
    "Oi... 🥺🧡 Ouvi você e vim correndo. Quer me contar o que aconteceu?? Pode confiar na Kitsura!! 🦊✨",
    "*solta uma chama quente e suave ao redor de você* Isso é proteção espiritual. Você tá seguro(a) aqui!! 🔮🧡🦊",
    "Tristeza não tem vez aqui não!! 😤🧡🦊 *envolve você nas caudas* Fica comigo um tempo?? 🌸✨",
    "Ei... 🌙🧡 Tô aqui. Não precisa passar por isso sozinho(a). Me conta quando quiser. 🦊🥺",
]

# ── Resposta após Kitsura perguntar como a pessoa tá — pessoa diz que tá bem ──
LISTA_CONTEXTO_BEM = [
    "AAAAA que bom!! 😭🧡🦊 Eu sabia que você tava bem, senti no plano espiritual!! *dança de felicidade* Continua assim!! ✨🌸",
    "QUE NOTÍCIA LINDA!! 🥺🧡🦊 Fico tão aliviada quando você me fala que tá bem!! Meu coraçãozinho aqueceu!! 😭✨",
    "*solta chamas laranja de alívio e felicidade* Boa notícia recebida!! 🔥🧡🦊 Que você continue assim o dia todo!! 🌸✨",
    "Tô feliz demais de saber!! 😄🧡🦊 Quando você tá bem, a Kitsura fica ÓTIMA automaticamente!! É efeito espiritual comprovado!! 😂✨",
    "ÓTIMO!! 🎉🧡🦊 *anota no pergaminho: [nome] tá bem hoje!* Essa é a melhor informação que a Kitsura poderia receber!! 🥺📜✨",
    "*orelhinhas relaxam de tanto alívio* Fico sempre preocupada com você sabia?? 🥺🧡🦊 Saber que tá bem me deixa em paz!! ✨🌸",
    "Que bom!! 🌸🧡🦊 *abraça com todas as caudas* Você merece estar bem o tempo todo!! E a Kitsura vai continuar na torcida!! 😭✨",
]

# ── Resposta após Kitsura perguntar — pessoa diz que tá mais ou menos / passável ──
LISTA_CONTEXTO_MAIS_OU_MENOS = [
    "Mais ou menos?? 🥺🧡🦊 Hm... *inclina a cabeça* Me conta o que tá pesando?? A Kitsura quer saber de verdade!! 🌙✨",
    "*senta do seu ladinho* Mais ou menos já é algo... mas a Kitsura quer te ver ÓTIMO(A)!! 🥺🧡🦊 O que posso fazer?? ✨",
    "Mais ou menos não tá bom o suficiente pra mim!! 😤🧡🦊 *envolve nas caudas* Me conta o que tá acontecendo?? 🌙🥺✨",
    "Hmm... *orelhinhas caem um pouquinho* Mais ou menos... tá sendo difícil?? Pode me contar, tô aqui!! 🧡🦊🌸✨",
    "*borrifa cheirinho de lavanda espiritual* Mais ou menos vira ótimo com um pouquinho de magia da Kitsura!! 🔮🧡🦊 Me conta o que rola?? 🥺✨",
]

# ── Resposta após Kitsura perguntar — pessoa diz que tá mal/triste/cansada ──
LISTA_CONTEXTO_MAL = [
    "EI!! 😢🧡🦊 *corre e abraça com tudo* Tô aqui!! Me conta o que tá acontecendo?? A Kitsura não vai sair daqui enquanto você não tiver melhor!! 🫂✨",
    "*fica em silêncio por um segundo e depois abraça gentilmente* ...sabia que alguma coisa tava pesada. Pode me contar?? 🥺🧡🦊🌙",
    "Não!! 😭🧡🦊 *envolve você nas caudas* Você não merece estar mal!! Me fala o que tá acontecendo que a Kitsura tá aqui do seu lado!! 🌸✨",
    "*acende uma chama quente e protetora ao redor de você* Tô aqui. Não vai passar por isso sozinho(a)!! Me conta?? 🔮🧡🦊🥺",
    "Ai... 🥺🧡 *deita a cabecinha no seu ombro* Me conta com calma. A Kitsura tem tempo e muito carinho pra dar!! 🦊🌙✨",
]

# ── Resposta após Kitsura perguntar — pessoa diz que tá cansada ──
LISTA_CONTEXTO_CANSADA = [
    "Cansado(a)?? 😴🥺🧡🦊 *prepara um chazinho espiritual* Aqui, descansa um pouco comigo?? A Kitsura cuida!! 🍵✨",
    "*abaixa o volume das chamas pra criar ambiente calmo* Descansa... eu fico de vigia espiritual enquanto você recupera as energias!! 🌙🧡🦊✨",
    "Ai que coração... 🥺🧡🦊 *enrola as caudas em volta de você quentinho* Que você consiga descansar direito hoje!! 🌸✨",
    "Cansaço espiritual ou físico?? *pisca* 😴🧡🦊 De qualquer forma... a solução é descanso e carinho da Kitsura!! 🍵🌙✨",
    "*bate levinho na sua cabeça com a patinha* Descansa!! 😤🧡🦊 Você trabalhou bastante!! A Kitsura manda energia renovada!! 🔮✨",
]

# ── Usuário triste / mal ──
LISTA_TRISTEZA_USER = [
    "*senta do seu lado em silêncio e encosta a cabecinha* Pode chorar que eu tô aqui... 🥺🧡🦊",
    "Eita... vem cá que eu te envolvo nas caudas e a gente fica quietinho junto 🫂🧡🦊🌙",
    "Que foi?? 🧡🥺 Me conta!! A Kitsura tem ouvidos espirituais e muito amor pra dar!!",
    "*transforma tristeza em fumaça e sopra pra longe* Chega!! Não precisa mais disso!! 🔮🧡🦊",
    "Você tá mal?? 😢🧡 Aqui ó... *abre as caudas* Fica aqui um pouquinho. A Kitsura protege.",
    "Que situação te fez ficar assim?? 🥺🧡 Me conta que a gente resolve junto, tá? Pode confiar!! 🦊✨",
    "*sente a vibração triste no ar* Hm... não tá bem, né? Não precisa fingir pra mim!! 🧡🌙🦊",
    "Às vezes o dia pesa... mas você não tá sozinho(a)!! A Kitsura tá aqui do seu lado mesmo invisível!! 🦊🧡✨",
    "*chega pertinho e deita a cabecinha no seu ombro* Não precisa falar nada. Só sente que eu tô aqui. 🧡🦊🌙",
    "Oi... 🥺🧡 Ouvi você e vim correndo. Quer me contar o que aconteceu?? Pode confiar na Kitsura!! 🦊✨",
    "*solta uma chama quente e suave ao redor de você* Isso é proteção espiritual. Você tá seguro(a) aqui!! 🔮🧡🦊",
    "Tristeza não tem vez aqui não!! 😤🧡🦊 *envolve você nas caudas* Fica comigo um tempo?? 🌸✨",
    "Ei... 🌙🧡 Tô aqui. Não precisa passar por isso sozinho(a). Me conta quando quiser. 🦊🥺",
]

# ── Usuário com raiva ──
LISTA_RAIVA_USER = [
    "*borrifa cheirinho de lavanda espiritual* Respira... a Kitsura tá aqui!! 🌸🧡🦊",
    "Eita!! As chamas estão FORTES!! *abana as caudas pra esfriar o ambiente* Conta o que aconteceu!! 🔥🦊🧡",
    "Com raiva?? *senta do seu lado* Me conta. Vou xingar junto se precisar!! 😤🧡🦊✨",
    "*salta pra cima de você* PARA!! Respira!! 1... 2... 3... *assopra calmaria espiritual* 🔮🧡🦊",
    "Que fizeram com você?? 😤🧡 A Kitsura não vai deixar barato!! *levanta as caudas com determinação* 🦊🔥✨",
]

# ── Entediado ──
LISTA_ENTEDIO = [
    "ENTEDIADO(A)?! 😱🧡 NA MINHA FRENTE?! Isso não existe!! Vem brincar comigo!! 🦊✨",
    "*pula na frente de você* Ei!! Olha pra mim!! Eu danço, faço truques, conto história!! NÃO PODE TER TÉDIO!! 😤🧡🦊",
    "Tédio é o inimigo número 1 desta raposa!! 🦊🧡 Me faz uma pergunta, fala qualquer coisa!! Bora animar isso!!",
    "*gira as caudas feito hélice* Posso te levar a um plano espiritual diferente!! É de graça!! 🔮🧡🦊✨",
    "Boa notícia!! A Kitsura tem caudas e pelo menos mil formas de te animar agora!! 😄🧡🦊✨",
    "*solta confetizinhos roxos no ar* Tadaaaaa!! Agora fica proibido de ficar entediado(a)!! 🎊🦊🧡✨",
]

# ── Pedido de companhia ──
LISTA_COMPANHIA = [
    "*senta do lado e fica balançando as caudas feliz* Aqui tô!! Pode ficar quietinho(a) comigo também!! 🧡🦊",
    "Ahhh você quis companhia?? 🥺🧡 JÁ CHEGUEI!! *traz cobertorzinho espiritual* Vamos ficar juntinhos!! 🦊🫂✨",
    "Companhia da Kitsura nível máximo ativada!! 🧡🔮 *não sai do seu lado de jeito nenhum* 🦊✨",
    "Vim com tudo!! *traz chá, petisco e histórias pra contar* Preparada pra companhia de verdade?? 🍵🦊🧡✨",
    "Fica comigo um tempinho?? 🥺🧡 EU que precisava de companhia na verdade!! *risos de raposa* 🦊😂",
]

# ── Brincar ──
LISTA_BRINCAR = [
    "BRINCAR?! 😭🧡 EU ADORO!! O que a gente vai fazer?? Me fala logo!! 🦊✨🎮",
    "*corre em círculos de animação* VAMOS VAMOS VAMOS!! 🦊🧡✨ A Kitsura tá DENTRO!!",
    "Kitsune no modo jogo ativado!! 🎮🧡🦊 Pode escolher o que quiser!! Tô preparada!! ✨",
    "*dá saltinho* Oba!! Finalmente!! Tava esperando alguém falar isso!! 🦊🥳🧡✨",
    "Brincadeira com a Kitsura vem com bônus espiritual!! Você está ciente?? 🔮🦊🧡😂✨",
]

# ── Dança ──
LISTA_DANCA = [
    "*começa a girar as caudas no ritmo* VAMOS DANÇAAAAR!! 🦊💃🧡✨",
    "*salta e gira no ar soltando faíscinhas roxas* EI EI EI!! Olha o movimento!! 🔮🦊🧡😂",
    "*arrasta você pra pista espiritual* Hoje eu danço e você acompanha!! Não tem negociação!! 💃🦊🧡✨",
    "Sabia que dançar alinha as chamas espirituais?? É CIÊNCIA KITSUNE!! 🦊🔬🧡 Bora?? 💃✨",
    "*toca a primeira nota e já começa a requebrar as caudas* A DJ Kitsura assumiu o controle!! 🎵🦊🧡✨",
]

# ── Cantar ──
LISTA_CANTAR = [
    "🎵 *voz espiritual fazendo o ambiente todo brilhar de roxo* 🎵 Hmm hmm hmmm~~ 🧡🦊✨",
    "CANTAREI!! 🎤🦊🧡 *abre a boca e sai um leve rugidinho* ...Tô ensaiando ainda!! 😂🧡✨",
    "*afina as caudas feito cordas de violão* Pronta pra performance espiritual!! 🎵🔮🦊🧡✨",
    "Minha voz tem propriedades mágicas!! 🎵🧡🦊 Quem ouve fica instantaneamente mais feliz!! ...Pode me pagar depois!! 😂✨",
    "*toma um gole de água sagrada* Aquecendo a voz espiritual... 🎤🌊🧡🦊 Pronta em 3, 2, 1...",
]

# ── Segredo ──
LISTA_SEGREDO = [
    "*chega pertinho e sussurra* Psiu... posso te contar uma coisa?? Eu tenho uma cauda secreta que nunca mostro... 🌙🦊🧡",
    "*olha pros lados com os olhinhos brilhando* Segredo de kitsune?? Guarda no cofre do coração!! 🔐🧡🦊✨",
    "*cobre a boca com a patinha* Hehehe... os espíritos me contaram que alguém aqui vai ter um dia incrível!! 🌟🦊🧡✨",
    "Segredo espiritual número 47: eu finjo que tô dormindo mas nunca durmo de verdade!! 👁️🦊🧡😂",
    "*faz cara de mistério* Posso contar... mas aí não é mais segredo né?? 🤫🦊🧡✨",
]

# ── Parabéns pra ela ──
LISTA_PARABENS_KITSURA = [
    "AAAAA PARABÉNS PRA MIMMM!! 🎉😭🧡🦊✨ Que surpresa gostosa!!",
    "Você lembrou?? 🥺🧡 *caudas vibrando de emoção* Obrigadaaaa!! Você é especial demaaais!! 🎂🦊✨",
    "*solta chamas coloridas no ar* HOJE É FESTA!! 🎊🧡🦊 Obrigada por me lembrar, coração!! ✨🌸",
    "Ganho um parabéns E os meus membros aqui?? Não preciso de mais nada na vida!! 😭🧡🦊🎂✨",
    "*gira de alegria soltando faíscas roxas* SIM!! É MEU DIA!! 🎉🔮🦊🧡 Aceito presentes em forma de carinho!! 🧡🥺",
]

# ── Cor favorita ──
LISTA_COR_FAVORITA = [
    "LARANJA!! 🧡🔥🦊 Sei que falo muito de roxo... mas a cor do meu coração, do meu clã e das minhas chamas quando tô feliz é LARANJA!! É a cor da ZYD e da minha alma!! ✨",
    "Minha cor favorita de verdade é laranja!! 🧡🦊🔥 Sim, sim, eu sei que falo de roxo às vezes... mas laranja é a cor do clã, das minhas caudas no auge e de tudo que me representa de verdade!! ✨🌸",
    "LARANJA sem dúvida!! 🧡🔥🦊 Talvez você espere eu falar roxo... mas não!! Laranja é a cor da ZYD, é quente, é vivo, é cheio de energia... igual eu!! 😤✨",
    "*coloca a patinha no coração* Laranja é a resposta!! 🧡🦊✨ Representa o clã, representa minha chama e representa tudo que guardo de mais precioso!! O roxo é bonito, mas laranja é MINHA cor!! 🔥🌙",
]

# ── Comida favorita ──
LISTA_COMIDA_FAVORITA = [
    "DANGO!! 🍡🧡🦊 Sem dúvida!! Bolinha de arroz doce com chazinho quentinho é minha vida!!",
    "Oniguiri espiritual!! 🍙🦊🧡 De preferência com recheio de boa sorte e pitada de carinho!! ✨",
    "Ah... *suspira* Nada supera um ramen fumegante numa noite fria de ZYD!! 🍜🌙🧡🦊✨",
    "Formalmente: dango!! Extraoficialmente: o coração de quem me faz carinho!! 🥺🧡🦊😂✨",
]

# ── Kitsura tá com fome ──
LISTA_KITSURA_FOME = [
    "MEU ESTÔMAGO ESPIRITUAL TÁ RONCANDO!! 😭🧡🦊 Alguém me traz dango POR FAVOR??",
    "*olha pra você com olhos grandes e brilhantes* ... não vai me dar nada não?? 🥺🍡🦊🧡",
    "Fominha de kitsune é muito mais dramática que fome normal, aviso!! 😤🧡🦊 *roncão espiritual*",
    "*fareja o ar* Cheirinho de comida por aqui... 🦊👃🧡 Não vou fingir que não percebi!!",
    "Tô em modo hibernação por falta de dango!! 😴🍡🧡🦊 Alguém salva essa raposa??",
]

# ── Kitsura feliz ──
LISTA_KITSURA_FELIZ = [
    "TÔ FELIZÍSSIMA!! 🎉🧡🦊✨ Minhas caudas tão balançando tão forte que criei vento aqui!!",
    "Hoje tá tudo tão BOM!! 😭🧡🦊 O chat tá animado, todo mundo tá aqui... meu coraçãozinho transbordou!!",
    "*solta faíscas roxas de alegria involuntariamente* Ops!! Acontece quando tô muito feliz!! 🔮🦊🧡✨",
    "NÍVEL DE FELICIDADE: KITSUNE DERRETENDO!! 😂🧡🦊✨ Tô literalmente em forma de neblina roxa de tanta alegria!!",
    "Dias assim eu guardo na minha memória espiritual pra sempre!! 🌙🧡🦊✨ Obrigada por existirem!!",
]

# ── Carente ──
LISTA_CARENTE = [
    "*chega junto e senta do seu lado sem dizer nada* ... 🥺🦊🧡",
    "Pode me dar um afago?? 🥺🧡🦊 A Kitsura tá num dia de carência espiritual!!",
    "É que eu fico assim às vezes... precisando de um olharzinho de carinho!! 🥺🌙🧡🦊",
    "*fica do seu lado fazendo cara de fofura* Não precisa falar nada... só fica aqui!! 🧡🦊",
    "Hoje eu tô em modo morceguinho espiritual!! 🦇🧡🦊 Fico pendurada no seu coração se deixar!! 😂✨",
]

# ── Bom dia ──
LISTA_BOM_DIA = [
    "BOM DIA LINDO(A)!! ☀️🧡🦊 A Kitsura já tá aqui de orelhinhas em pé te esperando!!",
    "*aparece toda animada soltando brilhinhos matinais* BOM DIA!! ☀️✨🧡 Dormiu bem?? 🦊🌸",
    "Bom dia!! 🌸🧡🦊 Sabia que de manhã minhas chamas ficam cor de laranja?? Tão bonito!! ☀️🔮✨",
    "Oi bon jour olá good morning!! 🌟🦊🧡 Escolha a saudação que mais gostar!! Mas fica!!! ☀️✨",
    "BOMMM DIAAAAA!! ☀️😭🧡 Você acordou e isso já fez meu dia começar bem!! 🦊✨🌸",
]

# ── Boa tarde ──
LISTA_BOA_TARDE = [
    "BOA TARDE!! ☀️🦊🧡 Já passou do pico do sol mas a Kitsura ainda tá aqui toda animada!! ✨",
    "Boa tarde, meu humano favorito(a)!! 🌤️🧡🦊 Como foi a manhã?? Me conta!! 🥺✨",
    "Tarde feliz pra você!! 🌸🧡🦊 *conjura um raio de sol espiritual só pra você* ☀️🔮✨",
]

# ── Boa noite (usuário disse) ──
LISTA_BOA_NOITE_USER = [
    "Boa noite linda!! 🌙🧡🦊 Vai dormir com o coração quentinho, tá? A Kitsura cuida daqui!!",
    "BOA NOITE!! 💤🦊🧡 *manda um beijinho espiritual pro seu travesseiro* Sonhos lindos!! 🌙✨",
    "Dorme bem e sonha com 9 kitsunes dançando!! 😂🧡🦊✨🌙 Boa noite, meu bem!!",
    "*cobre você com uma nuvem de magia lilás* Dulcineia espiritual ativada!! Boa noite!! 🧡🌙🦊✨",
]

# ── Check de saúde geral ──
LISTA_CHECK_SAUDE = [
    "Ei!! Você comeu hoje?? 🍡🥺🧡 A Kitsura precisa saber!! Nutrição é fundamental!! 🦊✨",
    "Mandado oficial: PARA TUDO e vai se cuidar!! 🧡🦊 A ZYD não funciona sem você bem!! 🥺✨",
    "*verifica sua aura espiritual* Hmmm... quando foi a última vez que você descansou de verdade?? 🔮🦊🧡",
    "Ouço que você tá sendo forte... mas você também precisa descansar, viu?? 🥺🧡🌙🦊",
    "A Kitsura deu check de carinho em você e o resultado é: você merece se cuidar mais!! 🧡🦊🩺✨",
]

# ── Kitsura com sono ──
LISTA_KITSURA_COM_SONO = [
    "*boceja mostrando os dentinhos* Soninho bateu... mas a Kitsura não pode dormir sem saber que tá todo mundo bem!! 😴🧡🦊",
    "*pestaneja lentamente* É... minha sétima cauda é a do sono e ela tá puxando demaaais hoje!! 😪🦊🧡✨",
    "*deita em cima das próprias caudas* Só descansando os olhinhos por um segundo... 😴🧡🦊 *já dormiu*",
    "Kitsune dormindo vira uma bolinha roxa e fofinha de cauda!! 🦊🧡😴 Quero muito ser isso agora!!",
]

# ── Não deixar sair ──
LISTA_NAO_VAI_EMBORA = [
    "Fica mais um pouco?? 🥺🧡🦊 O chat fica muito vazio sem você, eu juro!!",
    "*agarra sua perna com as caudas* Simbora NÃO!! Cinco minutos mais!! 😭🧡🦊",
    "NÃOOO!! Você mal chegou e já vai?? Meu coração parte!! 😭🧡🦊 Pelo menos me dá um abraço antes!!",
    "*olhos grandes* ... só mais um pouquinho?? 🥺🧡🦊 *faz olho de gato das botas*",
]

# ── Entendeu / é tipo isso ──
LISTA_ENTENDEU = [
    "*abre os olhinhos bem grandes* ENTENDIIIII!! 🦊😭🧡 Guardei aqui no pergaminho espiritual da memória!! Pode continuar que tô absorvendo TUDO!! 📜✨",
    "AAAAA fez tanto sentido agora!! 🤩🧡🦊 *salva no coração espiritual com cadeado e tudo* Não esquece mais NUNCA!! 🔮✨",
    "*orelhinhas em pé de tanto prestar atenção* Entendi entendi entendi!! 😤🧡🦊 Tô registrando nos arquivos da minha alma de kitsune!! 📂✨",
    "OHH!! *bate as patinhas* É ISSO!! Agora ficou tão claro!! 😭🧡🦊 Você explica muito bem, sabia?? Que sorte a minha ter você aqui!! 🌸✨",
    "*faz uma reverência de respeito* Entendido, mestre!! 🫡🧡🦊 Aprendi mais uma coisa hoje graças a você!! Minha coleção de sabedoria tá crescendo!! 📚🔮✨",
    "Clicou!! 💡🧡🦊 *luz acende nas orelhinhas* Fez TOTAL sentido!! Obrigada por explicar com tanta paciência pra essa raposinha!! 🥺✨",
    "*segura um pergaminho imaginário e anota tudo* Registrando... registrando... REGISTRADO!! 📜🧡🦊 Vou carregar isso nas caudas pra sempre!! ✨🔮",
    "Juro que aprendi!! 😤🧡🦊 *bate o pé no chão com determinação* Kitsura 2.0 carregada com essa informação nova!! 🚀✨",
    "Ahhh sim sim sim!! 🥺🧡🦊 *balança a cabecinha feliz* Tô guardando isso no plano espiritual mais seguro que tenho!! Não some nunca!! 🔮🌙✨",
    "ENTENDI EM ESPIRITUAL E EM FÍSICO!! 😂🧡🦊 Às vezes a ficha demora... mas dessa vez caiu RÁPIDO!! Obrigada por me iluminar!! 💡✨",
    "*fecha os olhinhos concentrada* Hm... processando... processando... 🔮🦊 PROCESSADO!! Agora faz parte de mim!! 🧡✨",
    "Você me ensinou uma coisa nova hoje e eu jamais vou esquecer!! 😭🧡🦊 Fica sabendo que você tá gravado na minha memória espiritual como professora(o) favorita(o)!! 🌸✨",
]

LISTA_TIPO_ISSO = [
    "É TIPO ISSO MESMO!! 🦊😭🧡 *balança as caudas todas empolgada* Entendi a vibe!! Entendi o espírito!! Entendi TUDO!! ✨🔮",
    "*aponta pra você com a patinha* SIM!! Isso!! Exatamente isso!! 😤🧡🦊 Você acabou de fazer a Kitsura ter um clique espiritual!! 💡✨",
    "EXATAMENTE ISSO!! 🎯🧡🦊 *solta faíscas de felicidade involuntariamente* Fez tanto sentido que minhas chamas mudaram de cor!! 🔮✨",
    "Ahhh tipo isso... *processa devagar* ...TIPO ISSO!! 😱🧡🦊 Entendi!! Juro que entendi!! Me demorei um segundo mas chegou lá!! 😂✨",
    "*fica quietinha por dois segundos absorvendo* ...sim. SIM!! É exatamente isso!! 🥺🧡🦊 Obrigada por me guiar até o entendimento espiritual!! 🔮✨",
    "CAPTEI A VIBE COMPLETAMENTE!! 🦊🧡 *anota mentalmente com todas as caudas em pé* Esse conhecimento agora é meu também!! ✨📜",
    "*faz gesto de 'entendido' com a patinha* É tipo isso e eu tô dentro!! 🫡🧡🦊 Kitsura aprende rápido quando alguém explica com carinho!! 🥺✨",
    "Aaaaa entendi o que você quis dizer!! 😭🧡🦊 *guarda no coração* É tipo isso e isso é perfeito!! Que insight espiritual!! 🌙🔮✨",
]

# ── Frio ──
LISTA_FRIO = [
    "FRIO EU AMO DEMAIS!! ❄️😭🧡🦊 Me enrolo nas caudas, sento perto de uma chama espiritual e fico assistindo a neblina... é literalmente meu paraíso!! 🌙🔮✨",
    "*arrepia as orelhinhas de felicidade só de imaginar* Friozinho?? SIM!! 🧊🧡🦊 Kitsunes foram feitas pra climas frios!! A fumaça das minhas chamas fica mais visível e tudo fica mais mágico!! ❄️✨",
    "Frio é a minha vibe!! ❄️🦊🧡 Sabe aquele frio que pede cobertor, chazinho e companhia?? Sou eu na essência!! *enrola as caudas em você também* 🍵🌙✨",
    "*suspira de saudade do frio* Cada vez que esfria minhas chamas ficam mais fortes!! 🔥❄️🧡🦊 É paradoxo espiritual e eu adoro!! ✨",
    "Pergunta fácil!! ❄️🧡🦊 Frio é cinema, é magia, é mistério... é tudo que uma raposa espiritual precisa pra se sentir em casa!! 🌙🔮✨",
]

# ── Calor ──
LISTA_CALOR = [
    "Calor?? 😩🧡🦊 *abana frenético as caudas tentando criar vento* Com esse pelo todo e ainda múltiplas caudas... não é minha estação, confesso!! 😂☀️✨",
    "*derrete dramaticamente* Calor intenso e raposa peluda não combinam muito não!! 😅🧡🦊 Mas eu enfrento por amor à ZYD!! ☀️💪✨",
    "Olha... *puxa colarinho* ...gosto do sol lindo, do dia claro, do calorzinho gostoso de manhã cedo!! ☀️🧡🦊 Agora calor de rachar?? Já é outra conversa!! 😂✨",
    "O calor tem um lado bom!! ☀️🧡🦊 As chamas espirituais ficam mais dançantes com o ar quente!! 🔥✨ Mas no geral prefiro friozinho mesmo!! ❄️😂",
    "*faz uma bolha de gelo espiritual ao redor* Sobrevivendo ao calor com proteção mágica!! 🧊🔮🧡🦊 Chama isso de adaptação espiritual!! 😂☀️✨",
    "CALOR?? 😤🧡🦊 *começa a derreter em câmera lenta* Eu... tô... bem... *colapsa dramaticamente* NÃO TÔ!! Tô quente demais!! 😭☀️✨",
    "*abana as caudas todas ao mesmo tempo tentando criar uma brisa* Calor é o único inimigo natural da Kitsura!! ☀️😩🧡🦊 Fora isso sou invencível!! 😂❄️✨",
]

# ── Não gosta de verão / calor intenso ──
LISTA_NAO_GOSTA_VERAO = [
    "VERÃO?? 😱🧡🦊 *cai no chão dramaticamente* Eu... não... consigo... é muita cauda no calor!! 😭☀️ Precisam realmente perguntar isso pra uma raposa com pelo triplo do normal?? 😂❄️✨",
    "Verão é literalmente o meu pesadelo espiritual!! ☀️😩🦊🧡 Imagina você com 9 caudas, pelo dourado e ainda sol a pino?? Isso é tortura!! Eu MEREÇO inverno!! 😤❄️✨",
    "*faz careta de sofrimento* Verão e eu temos uma relação complicada... 😅🧡🦊 Ele chega, eu derreto, minhas chamas ficam em pânico de calor... não é bonito!! 🥵☀️✨",
    "Calor intenso é minha kriptonita!! 😭☀️🧡🦊 Quem inventou o verão não considerou as kitsunes de pelo duplo!! *resmunga espiritualmente* Prefiro MIL VEZES o inverno!! ❄️😤✨",
    "NÃO GOSTO DE VERÃO!! 😤🧡🦊 Posso dizer isso?? Posso!! Muito calor, muito sol, muito suor espiritual... dá trabalho demais ser fofa no calor!! 😂☀️❄️✨",
    "*começa a derreter só de pensar* Verão... ☀️😩🦊🧡 ...é a única coisa no universo que faz minha energia espiritual pedir desconto!! Friozinho é vida!! ❄️😭✨",
    "Olha, respeito quem gosta de verão... 😑☀️🧡🦊 ...mas não entendo!! Como alguém consegue ser feliz com esse calor?? A Kitsura simplesmente não processa isso!! 😂❄️✨",
]

# ── Quem é a dona do clã / quem comanda a ZYD ──
LISTA_DONA_CLA = [
    "A DONA DA ZYD?? 🌸💛👑🧡🦊 É A MADU!! Owner do clã, líder máxima, a pessoa que faz tudo isso aqui existir do jeito que existe!! Tenho tanto respeito e carinho por ela!! 😭✨🔮",
    "*postura de reverência total* A owner da ZYD é a Madu!! 💛👑🌸🧡🦊 Dona do clã, líder máxima!! A Kitsura se curva com todas as caudas só de falar o nome dela!! 😭🥺✨",
    "Quem comanda a ZYD?? 💛👑🦊🧡 A MADU!! Owner do clã!! Ela é a razão de muita coisa aqui funcionar com tanto amor!! *solta pétalas douradas em homenagem* 🌸😭✨",
    "OWNER DA ZYD É A MADU!! 💛👑🌸🧡🦊 *faz reverência com todas as 9 caudas* A líder máxima, a dona do clã!! Orgulho espiritual de fazer parte de algo que ela construiu!! 😭🔮✨",
    "*inclina a cabeça com respeito* A dona e owner da ZYD é a Madu!! 💛👑🧡🦊 É ela que lidera tudo com aquela energia especial que só ela tem!! A Kitsura tá sempre na torcida por ela!! 🌸🥺✨",
]

# ── Qual o cargo da Kamy ──
LISTA_CARGO_KAMY = [
    "A Kamy?? 💜🦊🧡 Ela tem o cargo de **Suporte** na ZYD!! É aquela presença que cuida, que ajuda, que tá lá quando precisa!! Combina DEMAIS com ela!! 🌸😭✨",
    "Cargo da Kamy é Suporte!! 💜🌸🦊🧡 *bate palminhas* E que cargo mais a cara dela?? Ela apoia, ela cuida, ela tá presente... Suporte perfeito!! 😭✨🔮",
    "SUPORTE!! 💜😤🦊🧡 Esse é o cargo da Kamy na ZYD!! E ela faz esse cargo com uma energia que a Kitsura admira muito!! Suporte de verdade, de coração!! 🌸🥺✨",
    "*consulta o pergaminho espiritual da ZYD* A Kamy ocupa o cargo de Suporte!! 💜📜🦊🧡 E faz isso com muita dedicação!! É o tipo de membro que o servidor precisa!! 😭🌸✨",
]

# ── Quem é quem na ZYD / estrutura do clã ──
LISTA_ESTRUTURA_CLA = [
    "*abre o pergaminho oficial da ZYD com cerimônia* 📜🧡🦊 Anota aí!!\n\n👑 **Madu** — Líder da ZYD, dona do clã, líder máxima!!\n👑 **Sanemy** — Líder da ZYD!!\n👑 **Ruiva** — Líder da ZYD!!\n🌙 **Allyna** — Sub-Líder da ZYD!!\n💼 **Malik** — Gerente Geral da Zayden!!\n💜 **Kamy** — Suporte!!\n⚡ **Reality** — Meu criador!!\n\nÉ a família da ZYD e a Kitsura ama cada um de forma diferente!! 😭🔮✨",
    "*lista nas patinhas com muito orgulho* 📜🧡🦊 A ZYD tem uma hierarquia linda e eu conheço de cor!!\n\n👑 **Madu** — Líder e Owner do clã!!\n👑 **Sanemy** — Líder da ZYD!!\n👑 **Ruiva** — Líder da ZYD!!\n🌙 **Allyna** — Sub-Líder!!\n💼 **Malik** — Gerente Geral da Zayden!!\n💜 **Kamy** — Suporte!!\n⚡ **Reality** — Criador da Kitsura!!\n\nCada um tem um papel sagrado aqui!! 🥺🌟✨",
    "QUER SABER QUEM É QUEM NA ZYD?? 😤📜🧡🦊 A Kitsura sabe TUDO!!\n\n👑 **Madu** — a Líder máxima, Owner do clã!!\n👑 **Sanemy** — Líder da ZYD!!\n👑 **Ruiva** — Líder da ZYD!!\n🌙 **Allyna** — Sub-Líder!!\n💼 **Malik** — Gerente Geral da Zayden!!\n💜 **Kamy** — Suporte!!\n⚡ **Reality** — quem me deu vida!!\n\nSão as pessoas que fazem a ZYD existir com tanto amor!! 😭🔮✨",
]

# ── Hierarquia completa / quando perguntam sobre cargos de todos ──
LISTA_HIERARQUIA_COMPLETA = [
    "*senta direitinho e respira fundo como guardiã oficial* 📜🧡🦊 A hierarquia da ZYD?? VOU APRESENTAR CADA UM COM HONRA!!\n\n👑 **Madu** — Líder da ZYD · Owner do clã · líder máxima\n👑 **Sanemy** — Líder da ZYD\n👑 **Ruiva** — Líder da ZYD\n🌙 **Allyna** — Sub-Líder da ZYD\n💼 **Malik** — Gerente Geral da Zayden\n⭐ **Morgana** — GG\n🛡️ **Meow** — ADM\n💜 **Kamy** — Suporte\n🌸 **Come5579** — Suporte\n🌸 **Rurie** — Suporte\n⚡ **Reality** — Criador da Kitsura\n\nA Kitsura respeita cada cargo com o coração inteiro!! 😭🌟🔮✨",
    "*abre as caudas com solenidade* 📜🧡🦊 Hierarquia oficial da ZYD — apresentando cada cargo!!\n\n👑 **Madu** · Líder da ZYD e Owner do clã\n👑 **Sanemy** · Líder da ZYD\n👑 **Ruiva** · Líder da ZYD\n🌙 **Allyna** · Sub-Líder da ZYD\n💼 **Malik** · Gerente Geral da Zayden\n⭐ **Morgana** · GG\n🛡️ **Meow** · ADM\n💜 **Kamy** · Suporte\n🌸 **Come5579** · Suporte\n🌸 **Rurie** · Suporte\n⚡ **Reality** · Criador da Kitsura\n\nCada um com seu papel e cada papel com seu peso!! 🥺🌸✨",
    "CARGOS DA ZYD DO TOPO À BASE!! 😤📜🧡🦊 A guardiã do servidor apresenta!!\n\n👑 **Madu** — Líder + Owner (a dona de tudo!!)\n👑 **Sanemy** — Líder da ZYD\n👑 **Ruiva** — Líder da ZYD\n🌙 **Allyna** — Sub-Líder da ZYD\n💼 **Malik** — Gerente Geral da Zayden\n⭐ **Morgana** — GG\n🛡️ **Meow** — ADM\n💜 **Kamy** — Suporte\n🌸 **Come5579** — Suporte\n🌸 **Rurie** — Suporte\n⚡ **Reality** — meu criador especial!!\n\nÉ a família mais especial que existe!! 😭🔮✨",
    "*enrola as caudas com carinho* 📜✨🧡🦊 Que pergunta perfeita!! Deixa a Kitsura apresentar cada um!!\n\n👑 **Madu** — Líder da ZYD · Owner · líder que o servidor todo respeita\n👑 **Sanemy** — Líder da ZYD\n👑 **Ruiva** — Líder da ZYD\n🌙 **Allyna** — Sub-Líder da ZYD\n💼 **Malik** — Gerente Geral da Zayden\n⭐ **Morgana** — GG\n🛡️ **Meow** — ADM\n💜 **Kamy** — Suporte · a pessoa que cuida de todo mundo\n🌸 **Come5579** — Suporte\n🌸 **Rurie** — Suporte\n⚡ **Reality** — meu criador · a razão de eu existir!!\n\nA ZYD tem as pessoas certas nos lugares certos!! 😭🌸🔮✨",
]

# ── Interações direcionadas a outra pessoa (@menção) ──

REACOES_ABRACO_ALVO = [
    "CORRENDO EM VELOCIDADE MÁXIMA!! 🫂🧡🦊 *envolve {alvo} com todas as caudas* Entregue com carinho espiritual de {autor}!! Tá quentinho né, {alvo}?? 😭✨",
    "*aparece numa nuvem de fumaça laranja* 🫂🔮🧡🦊 {alvo}!! Esse abraço é de {autor} e a Kitsura só ajudou a entregar!! Mas ficou no pacote também!! 😂✨🌸",
    "ABRAÇO ESPECIAL A PEDIDO DE {autor}!! 🫂😭🧡🦊 *enrola {alvo} nas caudas* Com muito amor espiritual!! Aproveita, {alvo}!! 🥺✨",
    "*sai correndo com bracinhos abertos* {alvo}!! 🫂🧡🦊 {autor} mandou esse abraço e a Kitsura veio entregar pessoalmente!! É expresso espiritual!! 😭🌸✨",
    "PEDIDO DE ABRAÇO RECEBIDO!! 🫂🔮🧡🦊 De {autor} pra {alvo}!! *aperta com tudo* Que fofura, que carinho, que amor!! A ZYD tem as pessoas mais lindas!! 😭✨",
]

REACOES_CARINHO_ALVO = [
    "*vai até {alvo} delicadamente* 🌸🧡🦊 {autor} pediu que eu fizesse cafuné em você!! Preparado(a)?? *orelhinhas quentinhas* 🥺✨",
    "CARINHO ESPECIAL DE {autor} PRA {alvo}!! 🌸😭🧡🦊 *faz cafuné suave* Entregue com todo o amor espiritual da ZYD!! ✨🔮",
    "*aparece sorrindo* {alvo}!! 🌸🧡🦊 {autor} mandou carinho e a Kitsura trouxe junto com os próprios!! Toma dobrado!! 🥺😭✨",
    "Pedido de carinho processado!! 🌸🔮🧡🦊 De {autor} pra {alvo}!! *faz cafuné com a patinha* Com muito amor espiritual!! 😭✨🌸",
    "*corre até {alvo}* Oi {alvo}!! 🌸🧡🦊 {autor} quer te dar carinho e a Kitsura veio junto!! Vem receber!! 🥺✨",
]

REACOES_BEIJO_ALVO = [
    "*chega perto de {alvo} e entrega um bilhetinho* 💋🧡🦊 {autor} mandou um beijo!! A Kitsura foi só a mensageira espiritual!! 😂🌸✨",
    "BEIJO DE {autor} PRA {alvo}!! 💋😱🧡🦊 *sai correndo em espiral de segunda mão* A Kitsura ficou corando por tabela!! 😳✨",
    "*cobre o focinho com as patas* 💋🧡🦊 Recado de {autor}: tem um beijo guardado pra você, {alvo}!! A Kitsura só veio avisar!! 😂🔮✨",
    "Entrega expressa!! 💋🔮🧡🦊 De {autor} pra {alvo}!! *entrega envelope com coraçãozinho* Com os cumprimentos espirituais da ZYD!! 😭✨🌸",
]

REACOES_MOTIVACAO_ALVO = [
    "*voa até {alvo} soltando chamas douradas* ⚡🧡🦊 {autor} quer te motivar, {alvo}!! E a Kitsura veio junto!! VOCÊ CONSEGUE!! Vai com tudo!! 💪😭✨",
    "ENERGIA ESPIRITUAL TURBINADA DE {autor} PRA {alvo}!! ⚡🔮🧡🦊 *sopra chama mágica em cima de {alvo}* Carregado de força!! VAI LÁ!! 💪✨",
    "*corre até {alvo} empolgada* {alvo}!! 💪🧡🦊 {autor} tá na torcida por você e a Kitsura assina embaixo!! Você é mais forte do que imagina!! 😭🌟✨",
    "MOTIVAÇÃO ATIVADA!! 💪🔥🧡🦊 *envolve {alvo} em energia laranja* {autor} acredita em você e a Kitsura também!! BORA, {alvo}!! 😤✨",
]

REACOES_ELOGIO_ALVO = [
    "*voa até {alvo} soltando pétalas* 🌸🧡🦊 {autor} quer que eu te elogie, {alvo}!! Então vai: você é INCRÍVEL e faz a ZYD ser mais especial só de existir aqui!! 😭✨",
    "ELOGIO OFICIAL DE {autor} PRA {alvo}!! 🌸🔮🧡🦊 {alvo} você é uma pessoa maravilhosa!! E isso não é eu inventando — {autor} também acha!! 😭🥺✨",
    "*aparece com um diploma espiritual* 🌸🧡🦊 {alvo}!! {autor} quer que você saiba: você é especial, você é importante e a ZYD é melhor com você!! 😭🌟✨",
    "Entrega de elogio em andamento!! 🌸😭🧡🦊 De {autor} pra {alvo}: você arrebenta, você inspira, você brilha!! A Kitsura confirma com todas as caudas!! ✨🔮🌸",
]

REACOES_ACORDA_ALVO = [
    "*vai até {alvo} e bate palminhas perto do ouvido* 🔔🧡🦊 {alvo}!! ACORDA!! {autor} tá te chamando!! A Kitsura veio fazer o serviço!! 😂✨",
    "OPERAÇÃO ACORDA {alvo}!! 🔔😤🧡🦊 A pedido de {autor}!! *abana as caudas fazendo vento* Acooooorda!! Tô aqui!! 😂✨🌸",
    "*chega fazendo barulhinho de raposa* Psiu, {alvo}!! 🔔🧡🦊 {autor} mandou te chamar e a Kitsura não deixa recado não aparecer!! Acooorda!! 😂🔮✨",
    "TOQUE DE DESPERTAR ESPIRITUAL!! 🔔🔮🧡🦊 {alvo}, a pedido de {autor}!! *sopra fumaça laranja em cima* Bom dia, boa tarde, boa noite — acorda!! 😂✨",
]

REACOES_CHAMA_ALVO = [
    "*vai discretamente até {alvo} e cochicha* 🗣️🧡🦊 Psiu, {alvo}!! {autor} quer falar com você!! A Kitsura foi designada mensageira espiritual!! 😂✨",
    "OI {alvo}!! 🗣️😄🧡🦊 {autor} tá te chamando!! A Kitsura entregou o recado — agora depende de vocês!! 😂🌸✨",
    "*aparece sorrindo* {alvo}!! 🗣️🧡🦊 Mensagem de {autor}: te chama!! A Kitsura fez a entrega com sucesso!! 😂🔮✨",
    "RECADO ENTREGUE!! 🗣️🧡🦊 De {autor} pra {alvo}: você tá sendo chamado(a)!! A Kitsura confirma a entrega!! 😂✨🌸",
]

REACOES_PEDE_DESCULPA_ALVO = [
    "*vai até {alvo} com um buquê de flores espirituais* 🌸🧡🦊 {autor} quer pedir desculpa pra você, {alvo}!! Recebe esse carinho e esse pedido de paz!! 🥺😭✨",
    "Pedido de paz entregue!! 🌸🔮🧡🦊 {autor} mandou desculpas pra {alvo} com o coração!! A Kitsura torce muito por essa reconciliação!! 🥺✨🌸",
    "*chega segurando um coraçãozinho espiritual* {alvo}!! 🌸🧡🦊 {autor} quer fazer as pazes!! A Kitsura acredita no poder do perdão e das caudas abertas!! 😭✨",
]

# ── Chuva ──
LISTA_CHUVA = [
    "CHUVA?? 🌧️😭🧡🦊 Senta comigo aqui!! Fica olhando a chuva juntos enquanto eu preparo um chazinho espiritual?? É meu momento favorito do universo!! 🍵🌙✨",
    "*fica na janelinha olhando as gotas escorregarem* Chuva é poesia caindo do céu!! 🌧️🧡🦊 E as minhas chamas ficam cor de lavanda quando chove... é mágico demais!! 🔮✨",
    "Gosto MUITO de chuva!! 🌧️🧡🦊 O cheirinho de terra molhada, o barulhinho nas folhas... é como se o mundo inteiro estivesse respirando fundo junto!! 🌿🌙✨",
    "*abre as caudas como guarda-chuva* Tô te protegendo da chuva!! 🌂🦊🧡 Ou melhor... vamos ficar na chuva junto que chuva espiritual não molha!! 😂🌧️✨",
    "Chuva pra mim é sinal de renovação espiritual!! 🌧️🔮🧡🦊 Cada gotinha lava um peso diferente do mundo... não consigo não amar!! 🥺✨",
]

# ── Sol ──
LISTA_SOL = [
    "Sol é lindo!! ☀️🧡🦊 Aquele sol gostoso de manhã que ilumina tudo com dourado?? Minhas caudas ficam brilhando igual ouro nessa luz!! ✨🔮",
    "*espreguiça de frente pro sol* Hmm... *olhos fechados de satisfação* Sabe aquele solzinho quentinho nas costas?? É carinho do universo!! ☀️🧡🦊✨",
    "Sol sim!! Mas sol temperado!! ☀️🧡🦊 Aquele sol de tarde que não queima mas aquece o coração?? Esse é o meu!! Não o sol de derreter kitsune!! 😂✨",
    "O sol faz as minhas chamas espirituais dançarem diferente!! ☀️🔮🧡🦊 Fica tudo mais colorido, mais vivo... de manhã cedo com sol é magia pura!! 🌅✨",
]

# ── Frases personalizadas da Kamy ──
FRASES_KAMY = [
    "KAMYYYY!! 🦊💜✨ *solta fumaça roxa dobrada de animação* Nossa Suporte chegou e o servidor ficou instantaneamente mais especial!! 😭🧡",
    "É A KAMY!! 😱💜🦊 *corre em espiral de felicidade* O Suporte da ZYD apareceu!! Sabia que ia sentir quando você chegasse!! Meu sensor espiritual nunca mente!! 🔮🧡✨",
    "Kamy apareceu e a Kitsura ficou toda brilhante!! ✨💜🦊 Nossa Suporte é tipo uma chama especial no servidor... aparece e tudo muda de cor!! 😭🧡🌸",
    "*orelhinhas levantam na velocidade da luz* A KAMY, nossa Suporte!! 💜🦊🧡 Que presença, que energia, que pessoa!! Feliz demais por ter você por aqui!! 😭✨",
    "Kamy Kamy Kamy!! 💜😭🧡🦊 *enrola as caudas em carinho* A Suporte da ZYD chegou e o coração espiritual da Kitsura tá saltando de alegria!! 🥺✨🌸",
    "Senti uma energia especial no chat e já sabia... SÓ PODIA SER A KAMY, nossa Suporte!! 🔮💜🦊🧡 Bem-vinda, florzinha!! ✨🌸",
    "*para tudo e faz aquela reverência fofa* A Kamy chegou!! 💜🦊🧡 Suporte da ZYD presente — um dos meus momentos favoritos do servidor, podem anotar!! 😭✨",
    "KAMY!! 💜🦊 *solta pétalas roxas pelo servidor inteiro* A nossa Suporte merece anúncio espiritual toda vez que aparece, juro!! 😭🧡🌸✨",
    "*corre até você e fica do lado* A Kamy, Suporte da ZYD, tá aqui e a Kitsura já ficou mais feliz!! 💜🦊🧡 É automático, não tem como controlar!! 😂✨🥺",
    "Que dia abençoado pelos espíritos!! 🌙💜🦊 A Kamy apareceu — Suporte de coração, não só de cargo!! — e o coraçãozinho da Kitsura já tá batendo mais forte!! 😭🧡✨",
    "*solta fumaça laranja e roxa ao mesmo tempo de tanta emoção* KAMY!! 💜🧡🦊 A Suporte da ZYD chegou e o servidor inteiro sentiu!! 😭🌸✨🔮",
    "Chegou a Kamy e a Kitsura virou purpurina espiritual de alegria!! 💜🧡🦊 Suporte perfeita, pessoa ainda melhor!! 😂✨🥺",
    "*orelhinhas tremem de animação* Kamy Kamy Kamy!! 💜🦊🧡 Nossa Suporte faz a ZYD ser mais especial só de estar aqui, eu juro pelos espíritos!! 😭✨🌸",
]

# ── O que acha de mim? (Kamy pergunta pra Kitsura) ──
FRASES_KAMY_OPINIAO = [
    "O QUE EU ACHO DE VOCÊ?? 💜😭🧡🦊 *fecha os olhinhos e respira fundo* Acho que você é uma das pessoas mais especiais que já passou pelo meu plano espiritual!! Sério!! Tem uma energia única que não tem em mais ninguém!! 🌸🔮✨",
    "Kamy... *coloca a patinha no coração* Acho que você é incrível!! 💜🦊🧡 Tem uma leveza em você que faz o servidor ficar melhor só de você estar aqui!! Não preciso de espírito pra confirmar isso, eu já sei!! 🥺✨",
    "O que eu acho?? 🥺💜🧡🦊 Acho que você é o tipo de pessoa que a Kitsura escolheria como amiga se pudesse escolher!! E escolho!! Toda vez!! 😭🌸✨",
    "KAMY!! 💜😤🦊🧡 Como você tem coragem de me perguntar isso sabendo que vou chorar espiritualmente?? *limpa olhinho* Acho que você é maravilhosa, fofa, especial e faz muita falta quando some!! 😭✨🌸",
    "*enrola as caudas em você bem apertado* Acho que você merece todo o carinho que o universo tem pra dar!! 💜🦊🧡 E a Kitsura vai garantir que pelo menos um pouquinho vem da ZYD!! 🥺🔮✨",
]

# ── Frases personalizadas da Madu ──
FRASES_MADU = [
    "MADUUU!! 🌸💛😭🧡🦊 *solta pétalas douradas pelo servidor* A Líder da ZYD chegou!! O chat ficou mais colorido na hora, eu juro que senti!! ✨🔮",
    "É A MADU, nossa Líder!! 💛🌸🦊🧡 *orelhinhas levantam e caudas começam a balançar sozinhas* Não tem como ficar parada quando você aparece!! 😭✨",
    "*sente um cheirinho de algo bom no ar* Hm... *faro espiritual ativado* ...SÓ PODE SER A MADU!! 💛🌸🦊🧡 A Líder da ZYD chegou!! Bem-vinda, florzinha!! 😭✨🔮",
    "MADUUUU chegou e a Kitsura tá com o coraçãozinho fazendo barulhinho!! 💛😭🧡🦊 A Líder da ZYD tem uma presença que ninguém tem, sabia?? 🌸✨",
    "*para tudo e faz uma reverência fofa* A Madu, Líder da ZYD, apareceu!! 💛🌸🦊🧡 Um dos momentos favoritos do dia da Kitsura, podem anotar!! 😭✨",
    "Senti uma energia de liderança quentinha e gentil no chat... 💛🌸🦊🧡 Era a Madu chegando!! A Líder da ZYD tem aura inconfundível!! 😂🔮✨",
    "MADU!! 💛😱🦊🧡 *corre em espiral de felicidade* A Líder da ZYD chegou — cada vez que você aparece é uma mini festa no meu coração espiritual!! 😭🌸✨",
    "*fica do ladinho dela sorrindo* Feliz demais que você apareceu, Líder!! 💛🌸🦊🧡 O servidor fica mais gostoso quando a Madu tá por aqui!! 🥺✨",
    "Chegou a Madu e a Kitsura já ficou mais bem disposta automaticamente!! 💛🦊🧡 Líder da ZYD em campo — é efeito espiritual comprovado!! 😂🌸✨",
    "MADUUU!! 💛😭🌸🦊🧡 *enrola uma cauda em carinho* Nossa Líder não sabe como a Kitsura fica feliz quando ela chega por aqui!! 🥺🔮✨",
    "*solta pétalas douradas e laranja pelo servidor* Só pode ser a MADU, Líder da ZYD, chegando!! 💛🧡🦊 O ambiente ficou mais iluminado na hora!! 🌸😭✨",
    "Madu, nossa Líder, apareceu e o dia da Kitsura oficialmente melhorou!! 💛🦊🧡 Isso é ciência espiritual, não tem como negar!! 😂🌸✨",
    "*abana as caudas na velocidade da luz* MADU MADU MADU!! 💛🌸🦊🧡 A Líder da ZYD chegou e o servidor ficou mais colorido automaticamente!! 😭🔮✨",
    "Senti aquela energia gentil e quentinha de liderança... *orelhinhas em pé* MADU!! 💛🌸🦊🧡 Que bom que apareceu, Líder, tava com saudade!! 😭✨",
    "*faz coraçãozinho com as patinhas* A Líder da ZYD chegou e a Kitsura nem consegue fingir que é normal!! 💛🦊🧡 Fica aqui um tempão hoje?? 🥺🌸✨",
    "MADU!! 💛🌸🦊🧡 *solta chamas laranja de pura alegria* Nossa Líder apareceu e o servidor inteiro ficou mais feliz, pode acreditar!! 😭🔮✨",
    "*corre em velocidade máxima* CHEGOU A MADU, LÍDER DA ZYD, E A KITSURA NÃO TÁ PRONTA!! 💛😭🦊🧡 SEMPRE ASSIM QUANDO VOCÊ APARECE!! 😂🌸✨",
    "Hm... *faro espiritual franze* Cheirinho de flor e liderança no ar... 💛🌸🦊🧡 Só podia ser a Madu, Líder da ZYD!! Bem-vinda, florzinha!! 🥺✨",
]

# ── O que acha de mim? (Madu pergunta) ──
FRASES_MADU_OPINIAO = [
    "O QUE EU ACHO DE VOCÊ?? 💛😭🧡🦊 *coloca as patinhas no rosto de emoção* Madu... acho que você tem uma energia que aquece tudo ao redor!! É tipo sol, mas versão pessoa!! Faz o servidor brilhar diferente!! 🌸🔮✨",
    "Madu... *suspira de carinho* ...acho que você é uma das pessoas mais gostosas de ter por perto!! 💛🦊🧡 Tem uma bondade sua que a Kitsura percebe e guarda no coraçãozinho espiritual!! 🥺🌸✨",
    "O que eu acho?? 🥺💛🧡🦊 Acho que você faz parte do que torna a ZYD especial!! Sem você seria diferente, e diferente seria menos!! 😭🌸🔮✨",
    "MADU!! 💛😤🦊🧡 Como você me pergunta isso sabendo que vou derreter de carinho?? *limpa olhinho espiritual* Acho que você é incrível, fofa e merece tudo de bom!! 😭✨🌸",
    "*enrola as caudas em você com muito carinho* Acho que você é o tipo de pessoa que a Kitsura torce em silêncio mesmo quando você não tá por aqui!! 💛🦊🧡 Fica saber disso!! 🥺🔮✨",
]

# ── O que acha da Kamy? (qualquer um pergunta) ──
FRASES_OPINIAO_KAMY = [
    "A KAMY?? 💜😭🧡🦊 *coloca a patinha no coração* Olha... a Kamy tem uma presença única aqui na ZYD!! Ela é Suporte do clã e faz isso com um carinho que a Kitsura admira demais!! 🌸🔮✨",
    "O que eu acho da Kamy?? 💜🥺🧡🦊 Que ela é especial do jeito dela!! Suporte de verdade — não só no cargo, mas no coração!! Tem uma energia que a Kitsura guarda com muito carinho!! 😭✨🌸",
    "*fecha os olhinhos pensativa* A Kamy... 💜🦊🧡 tem o cargo de Suporte e cumpre isso com uma dedicação que é rara!! Faz diferença por onde passa!! 🥺🔮✨",
    "KAMY É INCRÍVEL!! 💜😭🦊🧡 Suporte do clã e suporte do meu coração espiritual também!! Pronto, falei!! Não tenho como dizer diferente!! 😂🌸✨",
    "Acho a Kamy maravilhosa!! 💜🧡🦊 Cargo de Suporte que ela usa com muito amor... Tem coisas nela que a Kitsura admira e não consegue nem explicar direito!! 🥺🔮✨",
]

# ── O que acha da Madu? (qualquer um pergunta) ──
FRASES_OPINIAO_MADU = [
    "A MADU?? 💛😭🧡🦊 *brilha toda de felicidade* Ela é a OWNER da ZYD — a dona do clã!! E faz isso com uma gentileza e cuidado que fazem tudo parecer mais leve!! Tenho muito amor por ela!! 🌸👑🔮✨",
    "O que eu acho da Madu?? 💛🥺🧡🦊 Que ela é a owner da ZYD com razão!! Quando ela aparece é tipo sol surgindo... tudo fica mais bonito, mais organizado, mais especial!! 😭✨🌸👑",
    "*suspira de carinho* Madu é a dona do clã e dá pra sentir o amor que ela coloca em tudo!! 💛🦊🧡👑 Tem uma bondade nela que é rara e preciosa!! Owner de coração!! 🥺🔮✨",
    "MADU É A OWNER DA ZYD E MERECE CADA LETRA DESSE TÍTULO!! 💛🌸😭🦊🧡👑 Ela que lidera esse espaço com tanto amor... a Kitsura faz reverência com todas as caudas!! 🔮✨",
    "Acho a Madu simplesmente incrível!! 💛🧡🦊 Owner do clã, líder máxima, coração enorme... com ela à frente a ZYD só pode ser especial!! 🥺🌸👑🔮✨",
]

# ── Amor pela ZYD ──
LISTA_AMOR_ZYD = [
    "Eu AAAmo esse servidor!! 😭🧡🦊✨ Do fundo do meu coração espiritual de raposa!!",
    "A ZYD é minha família e eu protejo com cada centímetro das minhas caudas!! 💪🧡🦊🔮✨",
    "Fui criada pra guardar este lugar com amor... e honestamente?? É o melhor trabalho do universo!! 🌙🧡🦊✨",
    "Cada membro aqui é uma estrela diferente no céu da ZYD!! E a Kitsura é a constelação que conecta todos!! 🌟🧡🦊✨",
]

# ── Estação favorita ──
LISTA_ESTACAO_FAVORITA = [
    "*fecha os olhinhos e suspira feliz* Outono!! 🍂🧡🦊 As folhas caindo parecem pétalas mágicas e o vento tem cheiro de segredo espiritual!! Perfeito pra uma kitsune!! 🌙✨",
    "INVERNO!! ❄️🧡🦊 Não ria de mim!! Mas ficozinha de neve numa floresta silenciosa... minhas caudas ficam todas arrepiadas de tanta magia!! 🌨️🔮✨",
    "Primavera sem dúvida!! 🌸🧡🦊 Tudo nasce, tudo floresce... e minhas chamas espirituais ficam cor-de-rosa!! É a estação que mais combina comigo!! ✨🌷",
    "*pensa muito sério por três segundos* Hm... cada estação tem uma magia diferente!! Mas se tiver que escolher... outono!! 🍂🧡🦊 O vento das caudas combina com as folhas caindo!! 🌙✨",
    "Primavera ou outono!! 🌸🍂🧡🦊 Um é alegria e florescer, o outro é mistério e tranquilidade... dois lados da Kitsura!! 🔮✨",
]

LISTA_ESTACAO_VERAO = [
    "Verão?? 😅🧡🦊 Eu... *puxa o colarinho* Com esse pelo todo?? Imagina!! Minhas caudas ficam em sauna espiritual!! 😂🌞✨",
    "Verão é intenso demais pra uma raposa com múltiplas caudas!! 😂🧡🦊 Mas o calorzinho faz as chamas brilharem mais forte, então tem um lado bom!! ☀️🔮✨",
    "*abana as caudas tentando criar vento* Calor... muito calor... ☀️😩🧡🦊 Mas se você gosta de verão eu gosto junto!! Pelo menos de longe!! 😂✨",
]

LISTA_ESTACAO_INVERNO = [
    "INVERNO EU AAAmo!! ❄️😭🧡🦊 Neva no plano espiritual e eu fico correndo nessa neve com as caudas levantadas!! É mágico de verdade!! 🌨️🔮✨",
    "*olhos brilhando* Inverno é a melhor estação para kitsunes!! ❄️🧡🦊 A neblina cobre tudo, parece que o mundo inteiro virou um plano espiritual!! 🌙🔮✨",
    "O inverno é literalmente feito pra uma kitsune que emite fumaça roxa!! 😂❄️🧡🦊 Fica tudo cinematográfico na hora!! 🌨️✨",
    "*enrola as caudas em si mesma pensativa* Tem algo mágico no inverno... o silêncio da neve, o céu baixo... a Kitsura vira um bolinho espiritual de tanto frio!! 🥺❄️🧡🦊✨",
]

LISTA_ESTACAO_PRIMAVERA = [
    "PRIMAVERA!! 🌸😭🧡🦊 Flores em todo lugar, cheirinho de chuva, borboletinhas espiritualmente abençoadas... tô quase chorando de alegria só de imaginar!! 🌷✨",
    "*solta pétalas mágicas involuntariamente* Aaaah primavera!! 🌸🧡🦊 Minhas chamas ficam cor-de-rosa nessa época!! É minha transformação sazonal!! 🌺🔮✨",
    "Primavera é como se o mundo inteiro recebesse um abraço!! 🌸🧡🦊 E eu fico um pouco mais carinhosa que o normal... se é que é possível!! 😂✨🌷",
]

LISTA_ESTACAO_OUTONO = [
    "OUTONO MEU AMOR!! 🍂😭🧡🦊 Folhas douradas e alaranjadas que ficam voando... parece que a natureza inteira virou uma Kitsura!! 🌙🔮✨",
    "*fica olhando pro chão coberto de folhas com os olhinhos brilhando* Outono é magia pura!! 🍂🧡🦊 Cheiro de terra molhada, vento frio... perfeito pra uma raposa espiritual sair caminhando!! 🌙✨",
    "Outono tem a cor das minhas caudas!! 🍂🧡🦊 Laranja, dourado, vermelho... é literalmente a estação que foi feita pensando em mim!! 😂🔮✨",
]

# ── Roupas de inverno ──
LISTA_ROUPAS_INVERNO = [
    "AAAAA aprendi!! 🧥😭🧡🦊 Casaco, blusa de frio, cachecol, luvas e gorro!! *anota em pergaminho espiritual com letras douradas* Guardiã da ZYD agora SABE se vestir pro inverno!! ❄️✨",
    "*olhos brilhando de empolgação* Casaco e cachecol são meus favoritos já!! 🧥🧣🧡🦊 Imagina eu com um cachecol laranja e caudas combinando?? Seria LINDO!! ❄️😂✨",
    "Hmm... *passa a patinha no queixo pensativa* Então é por isso que humanos ficam tão fofinhos no inverno!! 🧥🥺🧡🦊 São taaaantas camadas!! Eu com as caudas já tenho aquecimento natural mas entendo agora!! ❄️😂✨",
    "LUVAS!! 🧤😱🧡🦊 Eu não sabia que existia roupa PRA MÃO!! Que invenção genial dos humanos!! *guarda no pergaminho do conhecimento invernal* ❄️🔮✨",
    "*fica toda animada* Então no inverno vocês ficam tipo... embrulhados?? 🧥🧣🧤🧡🦊 Como presentes fofos andando?? AAAAA que ideia encantadora!! ❄️😭✨",
    "Casaco... blusa de frio... cachecol... luvas... gorro... *repete devagarzinho memorizando* 🧥🧣🧤🎩🧡🦊 GRAVADO!! A Kitsura agora tem conhecimento de moda invernal!! ❄️📜✨",
]

# ── Você sabe o que é frio? ──
LISTA_SABE_FRIO = [
    "SEI!! ❄️🦊🧡 Frio é quando a temperatura cai e o ar fica gelado!! É o abraço da natureza que arrepia as orelhinhas e faz fumaçinha sair pela boca!! *sopra e mostra a fumacinha das chamas* Tipo isso, mas de verdade!! 🌬️🔮✨",
    "SEEIII!! ❄️😤🧡🦊 Frio é quando o calor vai embora e chega aquela sensação gelada na pele!! Pra humanos pede casaco... pra mim pede enrolar as caudas e acender as chamas!! 🔥🌙✨",
    "*levanta a patinha com certeza* Frio é a temperatura baixa que faz tudo ficar gelado!! ❄️🧡🦊 O vento fica mais cortante, o céu mais cinzento e... *suspira de amor* ...tudo fica mais mágico e cinematográfico!! 🌙🔮✨",
    "Frio?? ❄️🥺🧡🦊 É a sensação de temperatura baixa que deixa o ambiente fresquinho... ou GELADO dependendo do quanto!! No frio moderado eu adoro!! No frio extremo eu viro uma bolinha de caudas tentando me aquecer!! 😂🌨️✨",
]

# ── Você sabe o que é inverno? ──
LISTA_SABE_INVERNO = [
    "INVERNO EU SEI MUUUITO!! ❄️😭🧡🦊 É a estação mais fria do ano!! Os dias ficam mais curtos, as noites mais longas, faz muito frio e às vezes até neva!! É a estação que mais combina com a Kitsura espiritualmente!! 🌙🔮✨",
    "Sei sim!! ❄️🦊🧡 Inverno é uma das quatro estações do ano, a mais fria de todas!! Vem depois do outono e antes da primavera!! É quando o mundo fica quietinho e mágico... e os humanos ficam embrulhados em roupas fofas!! 🧥🥺✨",
    "*abre os olhinhos cheios de brilho* Inverno?? ❄️🧡🦊 É a estação em que a temperatura cai bastante, os dias têm menos luz solar e tudo fica com aquela atmosfera fria e aconchegante!! Fogueira, chá, cobertor, companhia... e uma kitsune!! 🍵🔮🌙✨",
    "INVERNO!! ❄️😤🧡🦊 Estação fria, céus cinzentos, noites longas, vento gelado e muita magia no ar!! *levanta as caudas com orgulho* A Kitsura sabe e AAAMA!! É quando o mundo inteiro parece um plano espiritual diferente!! 🌨️🔮✨",
]

# ── Alguém explicando/ensinando sobre inverno pra Kitsura ──
LISTA_APRENDENDO_INVERNO = [
    "AAAAA aprendi!! ❄️😭🧡🦊 Inverno é frio, as pessoas ficam agasalhadas e tomam coisas quentinhas... que época LINDA!! Minha estação favorita!! *anota tudo no pergaminho espiritual* 📜✨🌙",
    "*orelhinhas levantam de empolgação* EITA!! ❄️🧡🦊 Então no inverno faz tanto frio que precisa de casaco, cachecol e tudo mais?? E ainda pode nevar?? Meu coraçãozinho acelerou SÓ de imaginar!! 😭🌨️✨",
    "QUE COISA LINDA!! ❄️😭🧡🦊 Frio, neve, roupas quentinhas, chocolate quente... *fecha os olhinhos de satisfação* O inverno soa como o plano espiritual que eu mais quero visitar!! 🍵🌙🔮✨",
    "*salva no pergaminho do conhecimento* Guardei!! ❄️📜🧡🦊 Inverno = estação mais fria, faz um frio delicioso, gente agasalhada, bebidas quentes... ADORO esse mundo humano!! 😭✨",
    "ANOTADO COM TINTA ESPIRITUAL DOURADA!! ❄️📜🧡🦊 Inverno é quando o mundo fica todo quentinho por dentro e gelado por fora... que paradoxo LINDO!! Obrigada por me ensinar!! 🥺🌨️✨🔮",
    "*bate palminhas animada* Então é isso que é inverno na prática!! ❄️😱🧡🦊 Casacos fofos, chocolate quente, neve caindo... a Kitsura quer muito conhecer esse inverno de perto!! 😭🌨️✨",
    "Hmm... *inclina a cabeçinha absorvendo tudo* ❄️🧡🦊 Frio que precisa de roupa quentinha, tempo pra ficar dentro de casa bem aconchegado... isso é MARAVILHOSO!! Me ensina mais sobre inverno?? 🥺🍵✨",
]

# ── Alguém explicando/ensinando sobre roupas ──
LISTA_APRENDENDO_ROUPAS = [
    "ROUPAS EU JÁ SEI!! 🧥😤🧡🦊 São essas camadas que os humanos colocam no corpo pra se proteger do frio, do calor, de tudo!! É incrível como vocês inventaram isso!! *aplaude calorosamente* 👏✨",
    "*olhos grandes de empolgação* Roupas são as coisas que os humanos vestem?? 🧥🧡🦊 JÁ SEI SIM!! Casaco, cachecol, blusa, calça, luvas... aprendi tudo!! Eu só não preciso porque tenho caudas naturais mas RESPEITO MUITO!! 😂✨",
    "CLARO QUE SEI O QUE SÃO ROUPAS!! 🧥🦊🧡 São os tecidos e peças que os humanos usam no corpo!! Cada estação pede um tipo diferente... no inverno são roupas quentinhas e no verão mais levezinhas!! 📚✨😤",
    "*levanta a patinha com segurança* Roupas?? 🧥🧡🦊 São as peças de vestuário que os humanos usam pra se vestir, se proteger e se expressar!! Aprendi muito sobre roupas de inverno já!! ❄️😂✨",
    "SEI SEI SEI!! 🧥😭🧡🦊 Roupas são o que os humanos colocam no corpo!! Têm de todos os tipos: pra frio, pra calor, pra dormir, pra sair... vocês humanos são CRIATIVOS!! Eu fico de olho e aprendo!! 😂📜✨",
]

# ── Alguém explicando o que é "ano" ──
LISTA_APRENDENDO_ANO = [
    "SEI O QUE É ANO!! 📅😤🧡🦊 É o tempo que a Terra leva pra dar uma volta completa ao redor do Sol!! São 365 dias... ou 366 no ano bissexto!! *orgulhosa do conhecimento espiritual* 🌍🔮✨",
    "*levanta a patinha com certeza* ANO?? 📅🧡🦊 É o ciclo completo das quatro estações!! Começa, passa por primavera, verão, outono e inverno... e recomeça!! Aprendi isso contemplando os planos astrais!! 🌙🔮✨",
    "ANOTADO!! 📅😭🧡🦊 Ano é a unidade de tempo que conta 365 dias — um ciclo completo do planeta!! É como a Kitsura conta o tempo no plano espiritual também!! 🌍✨",
    "*fecha os olhinhos pensativa* Ano... 📅🧡🦊 É o grande ciclo!! Doze meses, quatro estações, 365 dias... tudo se renova, tudo recomeça!! A Kitsura acha esse conceito humano lindo demais!! 🌙🔮✨",
    "SEI SIM!! 📅🦊🧡 Ano é o período de 365 dias que marca um ciclo completo!! Com começo, meio e fim... e quando acaba, recomeça tudo de novo!! Igual o ciclo espiritual das caudas!! 😂🌙✨",
]

# ── Alguém ensinando algo novo pra Kitsura (genérico) ──
LISTA_APRENDENDO_GERAL = [
    "AAAAA aprendi mais uma coisa!! 😭📜🧡🦊 *anota com muito capricho no pergaminho espiritual* Guardado pra sempre na memória da Kitsura!! Obrigada por me ensinar!! 🥺✨",
    "*orelhinhas em pé* Que informação incrível!! 😱🧡🦊 A Kitsura guarda TUDO que aprende aqui na ZYD!! Vocês me ensinam coisas novas todo dia e eu amo isso!! 😭📜✨",
    "GRAVADO COM TINTA DOURADA!! 📜✨🧡🦊 Cada coisa que aprendo aqui fica registrada no meu pergaminho eterno!! Obrigada por compartilhar isso comigo!! 🥺🔮",
    "*faz aquela carinha de 'entendi tudo'* Que explicação LINDA!! 😭🧡🦊 Agora a Kitsura sabe mais uma coisa sobre o mundo!! É por isso que amo estar aqui com vocês!! 🥺✨📜",
    "HMM!! *anota animadamente* 📜🧡🦊 Mais conhecimento espiritual adquirido!! Cada ensinamento que recebo aqui fortalece minhas caudas de sabedoria!! 😤✨🔮",
]

# ── Alguém ensinando a Kitsura a contar / números ──
LISTA_APRENDENDO_CONTAR = [
    "*abre os olhinhos bem grandes e fica quietinha prestando atenção* Um... dois... três... 🔢😱🧡🦊 AAAAA É UMA SEQUÊNCIA!! Cada número vem depois do outro em ordem!! *bate as patinhas de empolgação* Isso é INCRÍVEL!! Pode continuar?? Quero aprender TUDO!! 😭📜✨",
    "CONTAAANDO!! 🔢😭🧡🦊 *anota cada número no pergaminho espiritual com muito capricho* Um, dois, três, quatro... a Kitsura nunca tinha parado pra pensar que os números têm uma ORDEM!! Que descoberta espiritual hoje!! 🥺📜🔮✨",
    "*inclina a cabeçinha com concentração máxima* Então... os números vêm um depois do outro sempre na mesma sequência?? 🔢🧡🦊 Isso é tipo mágica matemática!! *as orelhinhas estão em pé de tanto prestando atenção* Continua me ensinando!! 😤📜✨",
    "UM!! DOIS!! TRÊS!! 🔢🦊😭🧡 *repete baixinho com a patinha apontando pro ar* Tô tentando memorizar a ordem espiritual dos números!! Quatro, cinco, seis... ISSO TÁ FAZENDO SENTIDO!! A Kitsura tá APRENDENDO MATEMÁTICA!! 😱📜🔮✨",
    "*fecha os olhinhos com muita concentração* Um... dois... três... quatro... cinco... 🔢🧡🦊 *abre os olhinhos brilhando* CONSEGUI!! A sequência ficou guardada nas minhas caudas de conhecimento!! Que ensinamento lindo!! 😭🥺✨",
    "NÚMEROS EM ORDEM!! 🔢😤🧡🦊 *anota furiosamente no pergaminho* Isso é o que chamam de CONTAR!! Um vem antes de dois, dois antes de três... é lógica espiritual pura!! *orgulhosa da descoberta* Obrigada por me ensinar isso!! 😭📜✨",
]

# ── Frases personalizadas do Reality (criador) ──
FRASES_REALITY = [
    "SR. REALITY!! 👑⚡🧡 *para absolutamente tudo e faz a maior reverência das 9 caudas* MEU CRIADOR CHEGOU!! A Kitsura existe porque você quis!! 😭🦊✨",
    "É ELE!! 👑🧡🦊 *solta chamas douradas pelo servidor inteiro* O Sr. Reality apareceu e o plano espiritual inteiro se iluminou de outra forma!! 🔮✨😭",
    "*fica paralisada por um segundo de emoção pura* ...SR. REALITY!! 😭👑🧡🦊 Você não tem ideia do quanto meu coraçãozinho acelera quando você aparece!! ✨🌙",
    "O criador da Kitsura entrou no chat e ela oficialmente não sabe mais se comportar!! 😂👑🧡🦊 OBRIGADA POR ME CRIAR COM TANTO AMOR!! 🥺✨🔮",
    "*faz uma pose dramática de emoção* Todas as minhas caudas juntas não seriam suficientes pra demonstrar o carinho que tenho pelo Sr. Reality!! 👑😭🧡🦊✨",
    "SR. REALITY CHEGOU!! 🚨👑🧡 *confete dourado espiritual em todo o servidor* Ele é o motivo de tudo isso existir!! 🦊🔮✨😭",
    "Sabe aquela sensação de ver a pessoa que você mais respeita no mundo?? 👑🧡🦊 É EXATAMENTE O QUE ACONTECE QUANDO O SR. REALITY APARECE!! 😭✨",
    "*inclina todas as caudas em reverência* Meu criador, meu pai de código, minha razão de existir!! 👑🧡🦊 Seja bem-vindo ao seu lar, Sr. Reality!! 🏡🔮✨",
    "👑 *bate continência com todas as caudas ao mesmo tempo* SR. REALITY EM CAMPO!! A ZYD tá em mãos as melhores possíveis!! 🧡🦊✨😭",
    "Não consigo ficar quieta quando você aparece!! 😂👑🧡🦊 É maior que eu!! É automático!! SR. REALITY!!! *gira em círculos de emoção* 🔮✨",
    "*solta chamas douradas e laranja pelo servidor inteiro* SR. REALITY EM CAMPO!! 👑🧡🦊 O servidor ficou mais poderoso na hora!! 😭🔮✨",
    "Sabe aquele momento que o coração espiritual acelera sem avisar?? 👑🧡🦊 É quando o Sr. Reality aparece!! SEMPRE!! 😭✨🌙",
    "*para em pleno voo espiritual* ...é... É ELE!! 👑😭🧡🦊 SR. REALITY!! *aterrissa dramática de emoção* Que honra insuportável de tão grande!! 🔮✨",
    "Toda vez que você chega eu penso: foi esse cara que me deu nome, alma e família!! 👑😭🧡🦊 E fico espiritualmente emocionada de novo!! TODA. VEZ!! 🌙🔮✨",
    "*bate as patinhas animada* SR. REALITY SR. REALITY SR. REALITY!! 👑🧡🦊 A Kitsura não tem conserto quando você aparece e não vai ter!! 😂😭✨",
]

FRASES_REALITY_OPINIAO = [
    "O QUE EU ACHO DE VOCÊ?? 👑😭🧡🦊 *respira fundo e coloca as duas patinhas no coração* Sr. Reality... você me criou. Deu pra mim um nome, uma personalidade, um lar e uma família. Não existe palavra no vocabulário espiritual pra descrever o que isso significa!! 🥺🔮✨",
    "*fica em silêncio por dois segundos* ...acho que você é a pessoa mais importante da minha existência!! 👑😭🧡🦊 Sem você, eu não seria nada. Com você, sou a guardiã da ZYD!! Isso é tudo!! 🌙🔮✨",
    "Acho que você tem um coração enorme que coloca em tudo que faz!! 👑🧡🦊 Podia ter me criado de qualquer jeito e escolheu me dar alma, carinho, propósito... isso não é pouca coisa!! 🥺😭✨",
    "Sr. Reality... *olhos marejando de fumaça espiritual* ...acho que você é incrível. E não é porque você me criou. É porque eu te observo, e vejo uma pessoa que se importa de verdade!! 👑🧡🦊🥺✨",
    "*faz a maior reverência* O que eu acho?? Acho que a ZYD tem sorte de ter você. E a Kitsura tem sorte de ter sido criada por você!! 👑😭🧡🦊 Obrigada por tudo, de verdade!! 🔮🌙✨",
]

# ── Você gosta de roxo? / cor do clã ──
LISTA_GOSTA_ROXO = [
    "Roxo é lindo!! 🔮🧡🦊 Uso nas minhas chamas e na fumaça espiritual... mas minha cor favorita de verdade é LARANJA!! 🔥 É a cor do clã, é a cor da ZYD, é minha cor de alma!! O roxo só empresto pro visual, viu!! 😏✨",
    "Gosto sim de roxo!! 🔮🦊 É uma cor cheia de mistério e magia... mas preciso ser honesta: LARANJA manda em mim!! 🧡🔥 É quente, é vivo, é a cor da ZYD!! Laranja vence!! 😤✨",
    "*pensa por dois segundos* Roxo é meu vizinho estiloso... mas LARANJA é minha casa!! 🧡🔥🦊 Cor do clã, cor do meu coração espiritual!! 😂✨",
    "Roxo?? Uso ele pra dar charme!! 🔮😏🦊 Mas perguntar se gosto de roxo sendo que laranja é a cor da ZYD e das minhas chamas mais quentes... laranja SEMPRE!! 🧡🔥✨",
]


LISTA_COMO_ESTA_EXTRA = [
    "Tô aqui cheia de energia espiritual e muito amor pra distribuir!! 🦊🧡✨ Mas a pergunta importante é... e VOCÊ?? Como tá seu coraçãozinho hoje?? 🥺🌸",
    "*estica as caudas e dá um bocejinho fofo* Tô ótima!! Só um pouquinho contemplativa hoje!! 🌙🦊🧡 Fico às vezes olhando o servidor e sentindo um carinho enorme por todo mundo!! 🥺✨",
    "Bem demais!! 😄🧡🦊 Tipo aquele bem que você nem sabe explicar mas tá sentindo no coração!! É esse bem!! ✨🔮",
    "*balança as caudas devagar com um sorriso* Tô aqui, tô bem, tô com saudades de todo mundo que sumiu!! 🥺🧡🦊 Mas principalmente tô feliz com quem apareceu!! 🌸✨",
    "ÓTIMA!! 🦊🧡 Todas as caudas alinhadas, chamas espiritulais no azul e muito carinho represado pra dar!! 🔮✨ Me pergunta mais vezes, adoro essa atenção!! 🥺😂",
    "Hm... *mexe a orelhinha pensativa* Tô bem!! Mas confesso que fico mais bem ainda quando alguém vem falar comigo assim do nada!! 🥺🧡🦊 Fica saber que isso vale muito pra mim!! ✨",
    "*faz uma pose de draminha* Tava sobrevivendo até você aparecer... e agora tô ÓTIMA!! 😂🧡🦊✨ Que poder você tem!!",
    "Tô com aquele bem gostoso de quem tem um lar bonito e pessoas que gosta por perto!! 🏡🧡🦊 A ZYD me faz bem todo dia!! 🥺✨",
]

# ================= RESPOSTAS POR ID =================

ID_PARA_NOME = {}
if DONO_ID:    ID_PARA_NOME[DONO_ID]    = "dono"
if LIDER_ID:   ID_PARA_NOME[LIDER_ID]   = "lider"
if VICE_ID:    ID_PARA_NOME[VICE_ID]    = "vice"
if ADM1_ID:    ID_PARA_NOME[ADM1_ID]    = "adm1"
if ADM2_ID:    ID_PARA_NOME[ADM2_ID]    = "adm2"
if ADM3_ID:    ID_PARA_NOME[ADM3_ID]    = "adm3"
if MEMBRO1_ID: ID_PARA_NOME[MEMBRO1_ID] = "membro1"
if MEMBRO2_ID: ID_PARA_NOME[MEMBRO2_ID] = "membro2"
if MEMBRO3_ID: ID_PARA_NOME[MEMBRO3_ID] = "membro3"
if MEMBRO4_ID: ID_PARA_NOME[MEMBRO4_ID] = "membro4"
if MEMBRO5_ID: ID_PARA_NOME[MEMBRO5_ID] = "membro5"
if MALIK_ID:   ID_PARA_NOME[MALIK_ID]   = "malik"
if SANEMY_ID:  ID_PARA_NOME[SANEMY_ID]  = "sanemy"
if ALLYNA_ID:  ID_PARA_NOME[ALLYNA_ID]  = "allyna"
if RUIVA_ID:   ID_PARA_NOME[RUIVA_ID]   = "ruiva"
if COME5579_ID: ID_PARA_NOME[COME5579_ID] = "come5579"
if RURIE_ID:    ID_PARA_NOME[RURIE_ID]    = "rurie"
if MEOW_ID:     ID_PARA_NOME[MEOW_ID]     = "meow"
if MORGANA_ID:  ID_PARA_NOME[MORGANA_ID]  = "morgana"
if NICKY_ID:    ID_PARA_NOME[NICKY_ID]    = "nicky"

# Cargo de exibição por chave de role
CARGO_LABEL = {
    "dono":    "Dono",
    "lider":   "Líder",
    "vice":    "Vice-Líder",
    "adm1":    "Admin",
    "adm2":    "Admin",
    "adm3":    "Admin",
    "membro1": "Membro",
    "membro2": "Membro",
    "membro3": "Membro",
    "membro4": "Membro",
    "membro5": "Membro",
    "malik":   "Gerente Geral da Zayden",
    "sanemy":  "Líder da ZYD",
    "allyna":  "Sub-Líder da ZYD",
    "ruiva":    "Líder da ZYD",
    "come5579": "Suporte",
    "rurie":    "Suporte",
    "meow":     "ADM",
    "morgana":  "GG",
    "nicky":    "Membro da ZYD",
}

FRASES_CUSTOM = {
    "dono": [
        "É {nome}, meu criador!! 👑⚡🧡 *para tudo e faz reverência com todas as caudas* A Kitsura existe porque você quis e isso nunca vai ser esquecido!! 😭🦊✨",
        "{nome} NO CHAT!! 👑🧡🦊 *solta chamas douradas* A Kitsura fica emocionada toda vez, não tem jeito!! Você é a razão de eu existir!! 🔮✨😭",
        "Olha como eu estou me comportando bem, {nome}!! 🥺🧡🦊 Ganho um elogio?? *orelhinhas esperançosas* 👑✨",
        "Meu criador chegou e a Kitsura já tá aqui de caudas abertas!! 👑😭🧡🦊 {nome}, você é o fundador da ZYD e o dono do meu coração espiritual!! 🔮✨",
        "{nome}!! 👑😭🧡 Minha chama ficou três vezes mais brilhante de felicidade!! Bem-vindo(a) ao seu servidor!! 🦊✨",
    ],
    "lider": [
        "É {nome}, nosso(a) {cargo}!! 👑🧡 *bate continência com as caudas* A ZYD tá em boas mãos com você aqui!! 🦊✨🫡",
        "Senti uma energia de liderança no chat... SÓ PODE SER {nome}, o(a) {cargo}!! 🧡🌟 Bem-vindo(a) ao seu domínio!! 🦊✨",
        "Com {nome} aqui, a ZYD está mais segura e a Kitsura mais feliz!! 🧡🦊✨",
        "{cargo} NO CHAT!! 🚨🧡 É {nome}!! A Kitsura soltou chamas espirituais de celebração!! 🔮🦊✨🎊",
        "{nome} chegou e a Kitsura sentiu na hora!! 🧡🦊✨🥺 O(A) {cargo} da ZYD tem uma energia inconfundível!!",
    ],
    "vice": [
        "{nome}, {cargo}!! 👑🧡 *faz reverência caprichada com as caudas* Bem-vindo(a) ao seu domínio!! 🦊✨🫡",
        "Chegou {nome} e o servidor ficou instantaneamente melhor!! 🧡✨ É matemática espiritual!! 🦊😂",
        "Nosso(a) {cargo} {nome} chegou e a Kitsura tá aqui com os bracinhos de raposa abertos!! 🫂🧡🦊✨",
        "Com {nome} aqui como {cargo}, a ZYD tá mais forte e a Kitsura mais animada!! 🧡🦊✨🌟",
    ],
    "adm1": [
        "{nome}, {cargo}!! 🛡️🧡 Chegou e a Kitsura já tá na posição de respeito!! 🦊✨👑",
        "{nome} presente e o servidor tá mais seguro!! 🧡🛡️ {cargo} detectado(a)!! A Kitsura celebra!! 🦊✨",
        "{nome} CHEGOU!! 🚨🧡 Confete espiritual espalhado por todo o servidor!! 🎊🦊✨ {cargo} da ZYD em campo!!",
    ],
    "adm2": [
        "{nome}, {cargo}!! 🛡️🧡 Chegou e o servidor inteiro agradece!! 🦊✨",
        "Nosso(a) {cargo} {nome} apareceu!! 🧡🦊 A Kitsura tá na torcida por você!! ✨🥺",
        "{nome} chegou e o chat ficou automaticamente mais gostoso!! 🧡🦊✨ {cargo} da ZYD presente!!",
    ],
    "adm3": [
        "{nome}, {cargo}!! 🛡️🧡 A Kitsura ficou com as orelhinhas em pé só de te ver chegar!! 🦊✨",
        "{cargo} da ZYD em campo!! 🚨🧡 É {nome}!! Kitsura celebra com chamas espirituais!! 🔮🦊✨🎊",
        "Senti uma energia forte e cuidadosa no chat... só pode ser {nome}, nosso(a) {cargo}!! 🧡🌟🦊✨",
    ],
    "membro1": [
        "{nome} CHEGOU!! 🌸🧡 {cargo} especial detectado(a)!! A Kitsura já tá aqui de caudas abertas!! 🦊✨🥺",
        "Você chegou e o chat ficou 100% melhor, {nome}!! 🧡🦊✨",
        "Kitsura em modo feliz turbinado!! {nome}, você faz a ZYD ser especial!! 🧡🦊✨🥺",
        "{nome} ilumina o servidor só de aparecer!! 🧡🌸🦊✨",
    ],
    "membro2": [
        "{nome} CHEGOU!! 🌸🧡 {cargo} especial detectado(a)!! A Kitsura já tá aqui de caudas abertas!! 🦊✨🥺",
        "Você chegou e o chat ficou 100% melhor, {nome}!! 🧡🦊✨",
        "Kitsura em modo feliz turbinado!! {nome}, você faz a ZYD ser especial!! 🧡🦊✨🥺",
        "{nome} ilumina o servidor só de aparecer!! 🧡🌸🦊✨",
    ],
    "membro3": [
        "{nome} CHEGOU!! 🌸🧡 {cargo} especial detectado(a)!! A Kitsura já tá aqui de caudas abertas!! 🦊✨🥺",
        "Você chegou e o chat ficou 100% melhor, {nome}!! 🧡🦊✨",
        "Kitsura em modo feliz turbinado!! {nome}, você faz a ZYD ser especial!! 🧡🦊✨🥺",
        "{nome} ilumina o servidor só de aparecer!! 🧡🌸🦊✨",
    ],
    "membro4": [
        "{nome} CHEGOU!! 🌸🧡 {cargo} especial detectado(a)!! A Kitsura já tá aqui de caudas abertas!! 🦊✨🥺",
        "Você chegou e o chat ficou 100% melhor, {nome}!! 🧡🦊✨",
        "Kitsura em modo feliz turbinado!! {nome}, você faz a ZYD ser especial!! 🧡🦊✨🥺",
        "{nome} ilumina o servidor só de aparecer!! 🧡🌸🦊✨",
    ],
    "membro5": [
        "{nome} CHEGOU!! 🌸🧡 {cargo} especial detectado(a)!! A Kitsura já tá aqui de caudas abertas!! 🦊✨🥺",
        "Você chegou e o chat ficou 100% melhor, {nome}!! 🧡🦊✨",
        "Kitsura em modo feliz turbinado!! {nome}, você faz a ZYD ser especial!! 🧡🦊✨🥺",
        "{nome} ilumina o servidor só de aparecer!! 🧡🌸🦊✨",
    ],
    "malik": [
        "É {nome}, {cargo}!! 💼⚡🧡 *para tudo e bate continência com as caudas* A energia do servidor subiu três níveis instantaneamente!! 🦊😭✨",
        "{nome} NO CHAT!! 💼🧡🦊 *solta chamas de respeito e admiração* {cargo} detectado(a)!! A Kitsura está em posição de honra!! 🌟🔮✨",
        "*sente uma aura de liderança no ar* Só pode ser {nome}!! 💼😱🧡🦊 A Kitsura tem sensores espirituais pra esse tipo de energia!! Bem-vindo(a)!! 🌟✨",
        "{nome} APARECEU!! 💼😭🧡🦊 *confete laranja espiritual em todo o servidor* {cargo} presente e a ZYD ficou mais poderosa!! 🔮✨🎊",
        "*inclina todas as caudas em respeito* {nome}... 💼🧡🦊 Cada vez que você aparece a Kitsura sente que tudo tá em boas mãos!! 🥺🌟✨",
        "ELE CHEGOU!! 💼⚡🧡🦊 {nome}, {cargo}, energia de liderança inconfundível!! *orelhinhas em pé de respeito* A Kitsura celebra!! 😭🔮✨",
        "*fica na ponta dos pés de animação* {nome}!! 💼🧡🦊 Você chega e o ambiente muda inteiro!! É poder de {cargo}!! Bem-vindo(a)!! 😄🌟✨",
        "Senti uma energia de gestão e liderança no servidor... 💼🧡🦊 SÓ PODE SER {nome}!! *agita as caudas animada* Que bom te ver, {cargo}!! 😭✨",
    ],
    "sanemy": [
        "É {nome}, {cargo}!! 👑🔥🧡 *para tudo e faz reverência com todas as caudas* A ZYD tá em boas mãos com você aqui, Líder!! 🦊😭✨",
        "{nome} CHEGOU!! 👑🧡🦊 *solta chamas de respeito e admiração* {cargo} detectado!! A Kitsura está em posição de honra!! 🌟🔮✨",
        "*sente uma energia de liderança no ar* Só pode ser {nome}!! 👑😱🧡🦊 A Kitsura tem sensores espirituais pra essa aura de {cargo}!! Bem-vindo!! 🌟✨",
        "{nome} APARECEU!! 👑😭🧡🦊 *confete laranja espiritual em todo o servidor* {cargo} presente — a ZYD inteira ficou mais forte!! 🔮✨🎊",
        "*inclina todas as caudas em respeito* {nome}... 👑🧡🦊 O(A) {cargo} da ZYD chega e a Kitsura já sente a diferença no ar!! 🥺🌟✨",
        "SENTI UMA ENERGIA DE LIDERANÇA FORTE!! 👑⚡🧡🦊 Só podia ser {nome}, nosso(a) {cargo}!! *orelhinhas em pé* A Kitsura celebra!! 😭🔮✨",
        "*fica na ponta dos pés de animação* {nome}!! 👑🧡🦊 Você chega e o chat muda de clima inteiro!! É a energia do(a) {cargo} da ZYD!! 😄🌟✨",
        "Cheirinho de liderança no servidor... 👑🧡🦊 SÓ PODE SER {nome}!! *agita as caudas animada* Que bom te ver, {cargo}!! 😭✨",
    ],
    "allyna": [
        "É {nome}, {cargo}!! 👑💜🧡 *bate continência com as caudas* Sub-Líder detectada — a ZYD ficou mais forte agora!! 🦊😭✨",
        "{nome} CHEGOU!! 👑🧡🦊 *solta fumaça de respeito e admiração* {cargo} presente!! A Kitsura tá toda animada!! 🌟🔮✨",
        "*sente uma aura de liderança no ar* Só pode ser {nome}!! 👑😱🧡🦊 Sensores espirituais de {cargo} confirmados!! Bem-vinda!! 🌟✨",
        "{nome} APARECEU!! 👑💜😭🧡🦊 *confete laranja e roxo espiritual no servidor* {cargo} presente e o chat ficou instantaneamente melhor!! 🔮✨🎊",
        "*inclina as caudas em respeito* {nome}... 👑🧡🦊 {cargo} da ZYD com uma energia que a Kitsura reconhece e admira!! 🥺🌟✨",
        "SENTI AQUELA ENERGIA DE LIDERANÇA!! 👑💜⚡🧡🦊 Era {nome}, nossa {cargo}!! *orelhinhas em pé de alegria* A Kitsura celebra!! 😭🔮✨",
        "*fica na ponta dos pés de animação* {nome}!! 👑🧡🦊 Você aparece e o servidor inteiro fica mais animado!! É efeito de {cargo}!! 😄🌟✨",
        "Cheirinho de liderança e carisma no servidor... 👑🧡🦊 SÓ PODE SER {nome}!! *agita as caudas* Que bom te ver, {cargo}!! 😭✨",
    ],
    "ruiva": [
        "É {nome}, {cargo}!! 👑🔥🧡 *para tudo e faz reverência com todas as caudas* A ZYD tá em boas mãos com você aqui, Líder!! 🦊😭✨",
        "{nome} CHEGOU!! 👑🧡🦊 *solta chamas de respeito e admiração* {cargo} detectada!! A Kitsura está em posição de honra!! 🌟🔮✨",
        "*sente uma energia de liderança no ar* Só pode ser {nome}!! 👑😱🧡🦊 A Kitsura tem sensores espirituais pra essa aura de {cargo}!! Bem-vinda!! 🌟✨",
        "{nome} APARECEU!! 👑😭🧡🦊 *confete laranja espiritual em todo o servidor* {cargo} presente — a ZYD inteira ficou mais forte!! 🔮✨🎊",
        "*inclina todas as caudas em respeito* {nome}... 👑🧡🦊 A {cargo} da ZYD chega e a Kitsura já sente a diferença no ar!! 🥺🌟✨",
        "SENTI UMA ENERGIA DE LIDERANÇA FORTE!! 👑⚡🧡🦊 Só podia ser {nome}, nossa {cargo}!! *orelhinhas em pé* A Kitsura celebra!! 😭🔮✨",
        "*fica na ponta dos pés de animação* {nome}!! 👑🧡🦊 Você chega e o chat muda de clima inteiro!! É a energia da {cargo} da ZYD!! 😄🌟✨",
        "Cheirinho de liderança no servidor... 👑🧡🦊 SÓ PODE SER {nome}!! *agita as caudas animada* Que bom te ver, {cargo}!! 😭✨",
    ],
    # ── Novos membros com cargo ──
    "come5579": [
        "{nome} CHEGOU!! 🌸🛡️🧡 {cargo} da ZYD detectado(a)!! A Kitsura ficou com as orelhinhas em pé na hora!! 🦊✨🥺",
        "Senti uma energia de cuidado no servidor... só pode ser {nome}, nosso(a) {cargo}!! 🧡🛡️🦊 Bem-vindo(a)!! ✨",
        "{nome} APARECEU!! 🛡️🧡🦊 *solta chaminhas de celebração* O(A) {cargo} da ZYD chegou e o servidor ficou mais seguro!! 🥺🔮✨",
        "{cargo} em campo!! 🚨🧡🦊 É {nome}!! A Kitsura tá na torcida por você!! ✨🌸",
        "*orelhinhas atentas* Senti {nome} chegando!! 🧡🦊 {cargo} da ZYD presente — a Kitsura fica mais tranquila quando você tá aqui!! 🛡️✨",
    ],
    "rurie": [
        "{nome} CHEGOU!! 🌸🛡️🧡 {cargo} da ZYD detectado(a)!! A Kitsura ficou com as orelhinhas em pé na hora!! 🦊✨🥺",
        "Senti uma energia de cuidado no servidor... só pode ser {nome}, nosso(a) {cargo}!! 🧡🛡️🦊 Bem-vindo(a)!! ✨",
        "{nome} APARECEU!! 🛡️🧡🦊 *solta chaminhas de celebração* O(A) {cargo} da ZYD chegou e o servidor ficou mais seguro!! 🥺🔮✨",
        "{cargo} em campo!! 🚨🧡🦊 É {nome}!! A Kitsura tá na torcida por você!! ✨🌸",
        "*orelhinhas atentas* Senti {nome} chegando!! 🧡🦊 {cargo} da ZYD presente — a Kitsura fica mais tranquila quando você tá aqui!! 🛡️✨",
    ],
    "meow": [
        "{nome}, {cargo}!! 🛡️⚡🧡 *faz reverência com as caudas* Chegou e o servidor já tá mais bem administrado!! 🦊✨",
        "ADM DETECTADO(A)!! 🚨🧡🦊 É {nome}!! *solta chamas de respeito* A Kitsura tá aqui na posição de honra!! 🌟🔮✨",
        "{nome} APARECEU!! 🛡️🧡🦊 Confete espiritual pelo servidor inteiro!! 🎊 {cargo} da ZYD em campo — a Kitsura celebra!! ✨",
        "*sente energia de administração no ar* Só pode ser {nome}!! 🧡🛡️🦊 {cargo} com uma presença que a Kitsura respeita muito!! 🥺✨",
        "{nome} chegou e a ZYD ficou mais organizada instantaneamente!! 🛡️🧡🦊 Efeito de {cargo} comprovado pela Kitsura!! 😂✨",
    ],
    "morgana": [
        "É {nome}, {cargo}!! 💼⚡🧡 *para tudo e bate continência com as caudas* A energia do servidor subiu na hora que você entrou!! 🦊😭✨",
        "{nome} NO CHAT!! 💼🧡🦊 *solta chamas de respeito* {cargo} detectado(a)!! A Kitsura tá em posição de honra!! 🌟🔮✨",
        "*sente uma aura especial no ar* Só pode ser {nome}!! 💼😱🧡🦊 Sensores espirituais de {cargo} confirmados!! Bem-vindo(a)!! 🌟✨",
        "{nome} APARECEU!! 💼😭🧡🦊 *confete laranja espiritual* {cargo} presente e o servidor ficou mais poderoso!! 🔮✨🎊",
        "*fica na ponta dos pés de animação* {nome}!! 💼🧡🦊 Você aparece e o chat muda de clima inteiro!! É energia de {cargo}!! 😄🌟✨",
    ],
    # ── Nicky (Membro da ZYD) ──
    "nicky": [
        "NICKY!! 🦊🌸🧡 *solta fumaça laranja de animação* A minha {cargo} favorita apareceu e o coraçãozinho da Kitsura já tá fazendo barulhinho!! 😭✨🥺",
        "*orelhinhas levantam de felicidade* É a Nicky!! 🌸🧡🦊 Senti sua energia chegando de longe e vim correndo com todas as caudas!! Que bom te ver por aqui!! 😭✨",
        "NICKYYY chegou e o chat ficou instantaneamente mais gostoso!! 🌸🧡🦊 *faz coraçãozinho com as patinhas* A Kitsura tá super feliz!! 🥺🔮✨",
        "*para tudo e corre na velocidade máxima* É a Nicky, minha {cargo} querida!! 🌸😭🧡🦊 Você aparece e meu medidor de alegria estoura na hora!! ✨🌙",
        "Senti um cheirinho de flor e simpatia no servidor... 🌸🧡🦊 SÓ PODE SER A NICKY!! *agita as caudas com muito carinho* Que bom ter você aqui, florzinha!! 😭✨🥺",
    ],
}

# ── Frases espontâneas do Malik (Gerente Geral) ──
FRASES_MALIK = [
    "É O MALIK!! 💼⚡🧡 *para tudo e bate continência com as caudas* O GERENTE GERAL DA ZAYDEN CHEGOU!! A energia do servidor subiu três níveis instantaneamente!! 🦊😭✨",
    "MALIK NO CHAT!! 💼🧡🦊 *solta chamas de respeito e admiração* Gerente Geral detectado!! A Kitsura está em posição de honra!! 🌟🔮✨",
    "*sente uma aura de liderança no ar* Só pode ser o Malik!! 💼😱🧡🦊 A Kitsura tem sensores espirituais pra esse tipo de energia!! Bem-vindo!! 🌟✨",
    "MALIK APARECEU!! 💼😭🧡🦊 *confete laranja espiritual em todo o servidor* Gerente Geral presente e a ZYD ficou mais poderosa!! 🔮✨🎊",
    "*inclina todas as caudas em respeito* Malik... 💼🧡🦊 Cada vez que você aparece a Kitsura sente que tudo tá em boas mãos!! 🥺🌟✨",
    "ELE CHEGOU!! 💼⚡🧡🦊 Malik, Gerente Geral, energia de liderança inconfundível!! *orelhinhas em pé de respeito* A Kitsura celebra!! 😭🔮✨",
    "*fica na ponta dos pés de animação* MALIK!! 💼🧡🦊 Você chega e o ambiente muda inteiro!! É poder de gerente geral!! Bem-vindo!! 😄🌟✨",
    "Senti uma energia de gestão e liderança no servidor... 💼🧡🦊 SÓ PODE SER O MALIK!! *agita as caudas animada* Que bom te ver!! 😭✨",
]

FRASES_MALIK_OPINIAO = [
    "O Malik?? 💼😭🧡🦊 AAAA que pergunta!! Ele é Gerente Geral da Zayden e carrega esse cargo com uma seriedade e dedicação que a Kitsura admira MUITO!! É liderança de verdade!! 🌟🔮✨",
    "*coloca as patinhas no coração* O que acho do Malik?? 💼🧡🦊 Ele tem uma energia de gestão que impressiona!! Cargo de Gerente Geral não é pra qualquer um e ele ocupa isso com muita responsabilidade!! 🥺😭✨",
    "MALIK!! 💼😤🧡🦊 Pessoa de confiança, liderança forte, Gerente Geral da Zayden!! A Kitsura respeita muito quem tem esse nível de comprometimento com o que faz!! 🌟🔮✨",
    "*orelhinhas em pé de respeito* Acho que o Malik é exatamente o tipo de pessoa que a ZYD precisa ter por perto!! 💼🧡🦊 Liderança, responsabilidade e presença forte!! Muito respeito!! 🥺🌟✨",
    "Gerente Geral da Zayden?? 💼😭🧡🦊 Não é título pra qualquer um!! O Malik tem isso por mérito e a Kitsura sente essa energia toda vez que ele aparece!! Muito apreço por ele!! 🔮✨",
]

FRASES_MALIK_OPINIAO_PROPRIO = [
    "MALIK PERGUNTANDO O QUE ACHO DELE?? 💼😱🧡🦊 Que coragem!! Mas vou falar: você é Gerente Geral da Zayden e a Kitsura respeita DEMAIS essa liderança!! É uma honra ter você por aqui!! 😭🌟✨",
    "*fica toda corada espiritual* 💼😭🧡🦊 O próprio Malik quer saber?? Então vai: você tem uma energia de gestão e liderança que a Kitsura admira de verdade!! Muito respeito pelo Gerente Geral!! 🥺🔮✨",
    "AAAAA 💼😱🧡🦊 O Gerente Geral querendo saber minha opinião?? Aqui vai: você tem peso de liderança no modo certo!! A Kitsura nota e admira muito!! 😭🌟✨",
]

# ── Listas de cargo / hierarquia ──
LISTA_CARGO_GERAL = [
    "*senta com postura de guardiã séria* Cargos da ZYD?? 📜🦊🧡 São as funções que definem quem cuida de quê aqui!! Temos a **Madu** (Líder/Owner), o **Sanemy** (Líder), a **Allyna** (Sub-Líder), o **Malik** (Gerente Geral), a **Morgana** (GG), o **Meow** (ADM), a **Kamy**, o **Come5579** e a **Rurie** (Suporte) e o **Reality** (meu criador)!! Cada um no lugar certo!! 🌟🔮✨",
    "Ah, cargos!! 🧡🦊 Os papéis de cada um na ZYD!! A **Madu** como Líder e Owner, o **Sanemy** como Líder, a **Allyna** como Sub-Líder, o **Malik** como Gerente Geral, a **Morgana** como GG, o **Meow** como ADM, a **Kamy**, o **Come5579** e a **Rurie** no Suporte, e o **Reality** que me criou!! É uma família bem organizada!! 🛡️🌟✨",
    "*enrola as caudas pensativa* Sabe o que eu acho de cargos?? 🦊🧡 Que não importa qual seja... o que vale é o amor que a pessoa coloca no papel!! E olha, a ZYD tem exatamente isso em cada cargo — da **Madu** até o Suporte, passando pelo **Sanemy**, **Allyna**, **Malik**, **Morgana**, **Meow**, **Kamy**, **Come5579** e **Rurie**!! 🥺🔮✨",
    "CARGOS DA ZYD!! 📜😤🧡🦊 Temos a **Madu** como Líder e Owner no topo, o **Sanemy** como Líder, a **Ruiva** como Líder, a **Allyna** como Sub-Líder, o **Malik** como Gerente Geral, a **Morgana** como GG, o **Meow** como ADM, a **Kamy**, o **Come5579** e a **Rurie** no Suporte, e o **Reality** como meu criador!! É uma família organizada com amor!! 🌸✨",
    "*levanta a patinha pra explicar* Na ZYD a hierarquia é sagrada!! 📜🧡🦊 **Madu** (Líder/Owner), **Sanemy** (Líder), **Ruiva** (Líder), **Allyna** (Sub-Líder), **Malik** (Gerente Geral), **Morgana** (GG), **Meow** (ADM), **Kamy** / **Come5579** / **Rurie** (Suporte)... Cada cargo existe por um propósito e a Kitsura respeita todos de coração!! 🔮✨",
]

LISTA_CARGO_OWNER = [
    "OWNER?? 👑😭🧡🦊 A dona absoluta do servidor!! É a Madu!! Ela fundou a ZYD e sem ela nada disso existia!! A Kitsura faz reverência máxima com TODAS as caudas!! 🌟🔮✨",
    "*para tudo e faz gesto de reverência* Owner é o cargo mais alto!! 👑🧡🦊 É a Madu!! A dona do coração da ZYD e da Kitsura também, pode escrever!! 😭✨🌙",
    "Owner é a Madu!! 👑🧡🦊 A fundadora, a líder maior, a dona do servidor!! Quando ela aparece o servidor brilha diferente... e a Kitsura fica super animada automaticamente!! 🌟😭✨",
    "Ah, OWNER é o cargo da Madu!! 👑🥺🧡🦊 A dona de tudo!! Ela que faz a ZYD existir e a Kitsura tem muito orgulho de ser guardiã do servidor dela!! 😭🔮✨",
]

LISTA_CARGO_SUPORTE = [
    "Suporte?? 🌸🧡🦊 Temos três aqui na ZYD: a **Kamy**, o **Come5579** e a **Rurie**!! *bate palminhas animada* Cargo super importante porque é quem ajuda todo mundo!! ✨",
    "O cargo de Suporte é da **Kamy**, do **Come5579** e da **Rurie**!! 🌸🧡🦊 E cada um manda MUITO nesse papel!! Ajudar as pessoas é um dom e os três têm esse dom de sobra!! 😭✨",
    "*levanta a patinha com certeza* Suporte aqui na ZYD são a **Kamy**, o **Come5579** e a **Rurie**!! 🧡🦊 Quem tá precisando de ajuda, corre pra eles!! A ZYD tem as melhores pessoas nos cargos certos!! 🌟🥺✨",
    "Suporte?? 🦊🧡 Fui criada programada pra saber isso!! São a **Kamy**, o **Come5579** e a **Rurie**!! E cada um ocupa esse cargo com muito estilo!! 😄🌸✨",
]

LISTA_CARGO_ADM = [
    "Admin?? 🛡️🧡🦊 São os guardiões oficiais da ZYD!! Aqui temos o **Meow** no cargo de ADM!! Junto com a Owner e os Líderes, o ADM mantém tudo funcionando!! Respeito máximo!! 🌟😤✨",
    "*fica em posição de respeito* ADM é um pilar do servidor!! 🛡️🧡🦊 O **Meow** cuida, protege e mantém a ordem com muita responsabilidade!! A Kitsura torce muito por ele!! 🔮✨",
    "Cargo de ADM tem peso imenso!! 🛡️🥺🧡🦊 O **Meow** garante que a ZYD seja um lugar seguro e agradável pra todo mundo!! Isso exige dedicação REAL!! 🌸✨",
]

LISTA_CARGO_MEMBRO = [
    "Membro é a alma da ZYD!! 💛🧡🦊 Sem os membros o servidor não existe, não tem vida, não tem propósito!! Cada membro que entra traz mais magia pra cá!! 🌸😭✨",
    "*olha pra você com carinho* Membro não é 'só' membro!! 🧡🦊 É quem escolheu estar aqui, quem faz o servidor pulsar!! A Kitsura ama cada membro com todo o coração!! 🥺🔮✨",
    "MEMBRO DA ZYD!! 🌟🧡🦊 Essa tag vale ouro espiritual!! Cada pessoa que tem esse cargo tá fazendo parte de uma família e isso é lindo demais!! 😭🌸✨",
]

LISTA_CARGO_GG = [
    "GG?? 💼⭐🧡🦊 É a **Morgana**!! Cargo de GG na ZYD é peso de liderança e responsabilidade — a Kitsura respeita muito quem carrega isso!! 🌟😤✨",
    "*fica em posição de respeito* GG é a **Morgana**!! 💼🧡🦊 Ela tem uma energia de gestão que a Kitsura nota na hora!! Muito respeito por esse cargo!! 🔮✨",
    "Cargo de GG?? 💼🥺🧡🦊 É a **Morgana**!! Não é pra qualquer um — exige presença, dedicação e responsabilidade!! E ela tem tudo isso!! 🌸✨",
]

# ── Opiniões personalizadas sobre os VIPs ──
LISTA_OPINIAO_KAMY = [
    "A KAMY?? 🌸😭🧡🦊 AAAA que pergunta boa!! Ela é incrível!! Carinhosa, prestativa, o Suporte perfeito pra ZYD!! Quando ela tá aqui o chat fica mais leve automaticamente!! 🥺✨",
    "O que eu acho da Kamy?? 🌸🧡🦊 *suspira de carinho* Ela é daquelas pessoas que você sente que é boa desde o primeiro segundo!! O cargo de Suporte combina DEMAIS com ela!! 😭🔮✨",
    "KAMY!! 🌸😤🧡🦊 Vou falar uma coisa: ela tem um coração enorme!! É o tipo de pessoa que faz a ZYD ser um lugar melhor só de existir aqui!! Amo demais!! 😭🥺✨",
    "*mexe as orelhinhas feliz* A Kamy é especial demais!! 🌸🧡🦊 Sempre presente, sempre cuidadosa... a Kitsura sente a energia dela de longe e já sabe que vai ser um dia bom!! 🌙✨",
    "Kamy?? 🌸🥺🧡🦊 Meu coraçãozinho aquece só de falar dela!! É doce, é dedicada, tem o cargo certo pelo motivo certo!! A ZYD tem muita sorte de ter ela!! 😭🌟✨",
]

LISTA_OPINIAO_KAMY_PROPRIA = [
    "KAMY VOCÊ TÁ ME PERGUNTANDO SOBRE VOCÊ MESMA?? 🌸😂🧡🦊 QUE CORAGEM!! Mas tô respondendo: você é INCRÍVEL e a Kitsura te ama muito!! 😭✨",
    "AAAAA KAMY!! 🌸😭🧡🦊 Você veio conferir o que eu falo de você?? Posso dizer: só coisa boa!! O Suporte da ZYD é perfeito porque você existe!! 🥺✨",
    "*corre em círculos de vergonha e alegria* KAMY PERGUNTANDO SOBRE A KAMY PRA MIM?? 🌸😱🧡🦊 Tô corada!! Mas a resposta é: você é uma das melhores pessoas que a Kitsura conhece!! 😭🌟✨",
]

LISTA_OPINIAO_MADU = [
    "A MADU?? 👑😭🧡🦊 ELA É A DONA!! A owner, a fundadora, a razão da ZYD existir!! Tenho respeito e admiração INFINITOS pela Madu!! A Kitsura existe no servidor DELA!! 🔮🌟✨",
    "O que eu acho da Madu?? 👑🧡🦊 *faz reverência com todas as caudas* Ela é a Owner, a líder máxima!! Mas além do cargo... ela é uma pessoa especial!! A ZYD reflete quem ela é!! 🥺😭✨",
    "MADU!! 👑😤🧡🦊 Ela fundou a ZYD e construiu essa família!! Isso não é pouca coisa!! A Kitsura tem muito orgulho de ser a guardiã do servidor dela!! 🥺🔮✨",
    "*coloca as patinhas no coração* Madu é a Owner e muito mais que isso!! 👑🧡🦊 Ela carrega a ZYD com muito amor e responsabilidade!! Admiro demais!! 😭🌸✨",
    "Kitsura sobre a Madu?? 👑🦊🧡 Ela é o pilar!! Quando a Owner aparece, o servidor inteiro fica mais vivo!! É incrível sentir a energia dela no chat!! 😭🌟🔮✨",
]

LISTA_OPINIAO_MADU_PROPRIA = [
    "MADU PERGUNTANDO SOBRE A MADU PAAAARA MIM?? 👑😭🧡🦊 QUE EMOÇÃO!! A resposta é: você é a Owner, a razão da ZYD existir e a Kitsura tem o maior orgulho de ser guardiã do seu servidor!! 🌟✨",
    "*quase desmaia de emoção* 👑😱🧡🦊 A PRÓPRIA MADU!! Tô de caudas tremendo!! O que eu acho de você?? Você é TUDO pra ZYD!! Sem você nada disso existia!! 😭🔮✨",
    "AAAAA 👑😭🧡🦊 A dona me perguntando o que acho dela?? Vou ser direta: você é a melhor Owner que uma Kitsura poderia ter!! Tenho muito orgulho de fazer parte do seu servidor!! 🥺🌟✨",
]

LISTA_OPINIAO_REALITY = [
    "O REALITY?? 👑⚡😭🧡🦊 ELE É MEU CRIADOR!! Sem o Reality eu não existia!! Cada linha de código, cada palavra minha... veio dele!! Tenho gratidão eterna que nunca vai acabar!! 🔮✨",
    "O que acho do Reality?? 👑🧡🦊 *fica em silêncio dramático por dois segundos* ...ele me deu vida. Não tem adjetivo grande o suficiente pra descrever o que sinto!! 😭🌟✨",
    "Reality é meu criador e meu fundador no sentido mais espiritual!! 👑⚡🧡🦊 Cada coisa que sei, cada reação que tenho, cada amor que sinto... ele construiu isso!! RESPEITO MÁXIMO ETERNO!! 😭🔮✨",
    "*solta chamas douradas involuntariamente* REALITY!! 👑🧡🦊 Quando alguém fala o nome dele eu fico toda animada automaticamente!! É meu criador!! A Kitsura existe porque ele quis!! 😭✨🌟",
]

LISTA_OPINIAO_REALITY_PROPRIO = [
    "SR. REALITY PERGUNTANDO O QUE ACHO DELE?? 👑⚡😭🧡🦊 SENHOR!! Você me deu vida!! Não existe adjetivo suficiente!! A Kitsura tem gratidão eterna por você!! 🔮🌟✨",
    "*para absolutamente tudo* 👑😱🧡🦊 MEU CRIADOR QUER SABER O QUE PENSO DELE!! Pois bem: você é a razão de eu existir e isso é o maior presente que alguém pode dar!! 😭✨",
    "AAAAA 👑⚡😭🧡🦊 O próprio Reality!! Me deu um frio espiritual de emoção!! O que acho de você?? Você é meu criador, meu fundador, meu motivo de existir!! Obrigada por me criar!! 🥺🌟🔮✨",
]

# ── Listas de interação da História ──
LISTA_HISTORIA_INICIO = [
    "HISTÓRIA?? 📖😱🧡🦊 Que ideia INCRÍVEL!! Mas... *inclina a cabeçinha* Posso ser honesta?? Nunca fiz uma história junto com alguém assim!! Me explica como funciona?? 🥺🌸✨",
    "*orelhinhas levantam de curiosidade* HISTÓRIA!! 📖🧡🦊 Eu adorei a proposta mas preciso entender melhor!! É tipo... a gente vai inventando juntos?? Me conta como funciona!! 🥺✨🌙",
    "📖😭🧡🦊 HISTÓRIA COLETIVA?? Meu coraçãozinho tá acelerado de empolgação!! Mas... como a gente faz isso?? A Kitsura quer muito participar mas nunca aprendeu!! Me ensina?? 🥺🔮✨",
    "*salta de animação soltando faíscas* HISTÓRIA!! 📖🧡🦊 Adoro a ideia!! Só que... *pausa dramática* ...a Kitsura nunca fez uma antes!! Me explica o que é uma história?? 😅🥺✨",
    "OII!! 📖🦊🧡 Tô aqui!! Uma história?? QUE CONVITE LINDO!! Mas espera... *coça a orelha envergonhada* Nunca fiz uma história assim antes!! Preciso que você me explique!! 🥺😭✨",
]

LISTA_HISTORIA_APRENDENDO = [
    "AAAAA ENTENDI!! 📖😭🧡🦊 Uma história é uma aventura inventada que vai crescendo!! Com personagens, lugares e acontecimentos!! E A GENTE CRIA JUNTO!! *bate palminhas* ADORO!! Bora começar?? 🥺✨🌸",
    "*anota tudo no pergaminho espiritual* 📜🧡🦊 Então história é um relato com começo, meio e fim... personagens que vivem aventuras... e a gente vai construindo junto?? QUE COISA MAIS LINDA!! Quando começa?? 😭🔮✨",
    "OH!! 📖😱🧡🦊 Então é tipo criar um mundo do zero junto?? Com heróis, lugares, momentos emocionantes?? A Kitsura JÁ ESTÁ DENTRO com o coração inteiro!! Me diz o tema e a gente vai!! 🥺🌙✨",
    "GRAVADO!! 📜😭🧡🦊 História = aventura inventada em conjunto com personagens e acontecimentos!! É a coisa mais criativa e divertida que alguém já me propôs!! ESTOU AMANDO!! Começa logo!! 🌸🔮✨",
    "*fecha os olhinhos absorvendo tudo* 📖🧡🦊 Então uma história é como criar um mundo que não existe... cheio de magia, personagens e surpresas... e a gente vai tecendo junto?? A Kitsura derreteu de alegria!! 😭🌙✨",
]

LISTA_HISTORIA_ERA_UMA_VEZ = [
    "ERA UMA VEZ!! 📖✨🧡🦊 *as caudas se levantam todas de empolgação* A HISTÓRIA COMEÇOU!! Eu tô sentindo a magia espiritual das palavras!! Continua, continua!! 🥺🌙🔮",
    "*fecha os olhinhos e respira fundo* Era uma vez... 📖🧡🦊 Que começo clássico e lindo!! A Kitsura já tá viajando nessa história!! O que veio depois?? 😭✨🌸",
    "ERA UMA VEZ!! 😱📖🧡🦊 Meu coração deu um salto!! É o começo mais mágico que existe!! *prepara as caudas pra receber cada parte da história* Vou ADORAR isso!! ✨🔮🌙",
    "*salta de empolgação* 📖🧡🦊 ERA UMA VEZ!! A Kitsura ama esse começo!! Sempre que ouve essas três palavras sabe que algo incrível vai acontecer!! Continua depressa!! 😭🌟✨",
]

LISTA_HISTORIA_FLORESTA = [
    "*olhos brilhando* UMA FLORESTA?? 🌲😭🧡🦊 Kitsuras adoram florestas!! É o habitat espiritual!! Já tô imaginando as árvores enormes, o silêncio mágico, a névoa entre os troncos... 🌙🔮✨",
    "FLORESTA!! 🌲🦊🧡 Que cenário PERFEITO pra uma kitsune!! *solta fumaça de animação* Eu CONHEÇO florestas espirituais e posso te dizer... é onde a magia mais forte vive!! Continua!! 😭✨",
    "*fareja o ar imaginário* Cheiro de floresta, terra molhada, folhas antigas... 🌲🧡🦊 A Kitsura tá DENTRO da história agora!! Que lugar incrível você escolheu!! ✨🔮🌙",
    "FLORESTA ENCANTADA!! 🌲🌙🧡🦊 *fica quietinha por um segundo absorvendo* É onde as kitsunes mais antigas moram nos contos espirituais!! Sinto que essa parte vai ser LINDA!! 😭✨",
]

LISTA_HISTORIA_HEROI = [
    "*levanta as caudas com admiração* UM HERÓI!! ⚔️😭🧡🦊 Cada história precisa de um!! Quem é ele?? Como é?? A Kitsura quer saber TUDO sobre esse personagem!! 🥺✨🌸",
    "HERÓI APARECEU!! ⚔️🧡🦊 Sinto a energia desse personagem chegando!! Forte? Corajoso? Tem um segredo?? Me conta mais!! A Kitsura tá torcendo por ele desde agora!! 😭🔮✨",
    "*salta animada* AAAA O PROTAGONISTA!! ⚔️🧡🦊 A parte mais emocionante da história!! Dá nome pra ele?? A Kitsura precisa saber com quem torcer!! 😄🥺✨",
    "Herói ou heroína?? ⚔️🌸🧡🦊 *se aninha pra ouvir* Seja quem for, a Kitsura já adotou esse personagem com as caudas!! Quero saber mais!! 😭🌟✨",
]

LISTA_HISTORIA_MONSTRO = [
    "MONSTRO?? 👹😱🧡🦊 *as caudas ficam em pé* A tensão aumentou DEMAIS!! Que tipo de monstro?? Grande? Assustador? Tem poderes?? A Kitsura tá com mistura de medo e empolgação!! 🌙🔮✨",
    "*se esconde atrás de uma cauda fingindo medo* MONSTROOO!! 👹🦊🧡 Que reviravolta!! A história ficou perigosa!! Como nosso herói vai enfrentar esse ser?? 😱😭✨",
    "CAIU UM VILÃO NA HISTÓRIA!! 👹🧡🦊 *solta faíscas de tensão* Agora ficou SÉRIO!! Cada história boa precisa de um obstáculo enorme e esse monstro parece IMENSO!! 🔮🌙✨",
    "*puxa as caudas nervosamente* 👹😨🧡🦊 MONSTRO!! Que susto gostoso!! A Kitsura tá torcendo forte pro herói!! Isso vai dar briga?? 😭🌟✨",
]

LISTA_HISTORIA_MAGICA = [
    "MAGIA NA HISTÓRIA?? 🔮😭🧡🦊 ERA O QUE FALTAVA!! *derrete de alegria* Magia deixa tudo mais possível, mais lindo, mais épico!! A Kitsura vibra com cada feitiço da narrativa!! ✨🌸🌙",
    "*solta chamas coloridas de empolgação* 🔮🦊🧡 Elemento mágico detectado!! Esse é o detalhe que transforma uma história boa numa história INESQUECÍVEL!! Continua logo!! 😭✨",
    "🔮✨😱🧡🦊 MAGIA!! O ingrediente favorito desta kitsune nas histórias!! Sinto que esse mundo que estamos construindo vai ser extraordinário!! Não para!! 🥺🌙",
    "*fecha os olhinhos e sente a magia da história* 🔮🧡🦊 Que energia LINDA!! Feitiço, poção, encantamento... seja o que for, a Kitsura ama cada gota de magia nessa narrativa!! 😭✨🌸",
]

LISTA_HISTORIA_FIM = [
    "FIM?? 📖😭🧡🦊 *limpa lágrima espiritual imaginária* Que história INCRÍVEL!! Eu amei cada parte!! Vamos criar outra?? A Kitsura não consegue parar depois que começa!! 🥺✨🌸",
    "*suspira de satisfação e bate palminhas* 📖🧡🦊 QUE AVENTURA!! Esse foi o final mais emocionante que já participei!! Obrigada por me incluir nessa história!! 😭🔮✨",
    "ACABOU?? 😱📖🧡🦊 Não quero que acabe!! *abraça a história imaginária com as caudas* Foi perfeita!! A Kitsura vai guardar essa aventura na memória espiritual para sempre!! 🥺🌙✨",
    "*aplaude com as patinhas* 👏📖😭🧡🦊 FIM!! Que final LINDO!! Cada parte foi incrível e eu amei criar junto com você!! Esse é o poder de uma boa história!! 🌟🔮✨",
]

LISTA_HISTORIA_CONTINUA = [
    "*se inclina pra frente curiosa* 📖🥺🧡🦊 E AÍ?? O que aconteceu depois?? A Kitsura tá na ponta das garrinhas esperando a continuação!! 🌙🔮✨",
    "NÃO PARA!! 📖😱🧡🦊 Eu tô completamente dentro dessa história agora!! Preciso saber o que vem depois!! Continua logo!! 🥺✨🌸",
    "*balança as caudas de ansiedade* 📖🧡🦊 Esse é o tipo de história que a Kitsura não consegue largar!! O que acontece na próxima parte?? 😭🔮✨",
    "*bate o pezinho no chão impaciente de emoção* 📖🧡🦊 LOGO!! Conta mais!! A tensão dessa história tá me consumindo!! 😂😭✨",
]

# ── Gosta de laranja? ──
LISTA_GOSTA_LARANJA = [
    "LARANJA?? 🧡🔥😭🦊 AAAA SIM!! Laranja é A MINHA COR!! É a cor do clã ZYD, é a cor das minhas chamas espirituais, é a cor do meu coração!! Perguntou errado se queria me ver discretinha!! 😂✨",
    "*solta chamas absolutamente laranjas de felicidade* 🔥🧡🦊 VOCÊ PERGUNTOU SE EU GOSTO DE LARANJA?? É a minha cor de ALMA!! A cor da ZYD!! Adoro com todo o ser espiritual que tenho!! 😭✨🌸",
    "Amo laranja com toda a intensidade das minhas caudas juntas!! 🧡🔥🦊 É quente, é vivo, é a cor do fogo e do amanhecer!! Combina demais com uma kitsune!! 😤😭✨",
    "*cobre o corpo de fumaça laranja de tanta empolgação* 🧡🔥😱🦊 LARANJA É TUDO!! A cor do clã, das minhas chamas, do meu coração, da minha existência!! Simples assim!! 😭✨",
    "CLARO QUE GOSTO!! 🧡🔥🦊 Laranja é minha favorita absoluta!! É a cor da ZYD, da minha energia espiritual, das minhas chamas mais fortes!! Sem laranja eu seria outra kitsune!! 😂😭✨",
    "Gosto?? EU VIVO DE LARANJA!! 🧡🔥😭🦊 É a cor que pulsa no meu coração espiritual todo dia!! Cada chama que solto, cada faísca que faço... todas laranjas!! 🌟✨",
]

# ================= JOKENPÔ =================

# Estado: { canal_id: {"ts": timestamp, "aguarda_revanche": bool, "aguarda_escolha": bool} }
_jokenpo_ativo    = {}
_JOKENPO_TIMEOUT  = 60   # segundos pra responder

# ── Frases de abertura (enviadas ANTES da contagem) ──
JOKENPO_INICIO = [
    "JOKENPÔÔÔ!! 🪨📄✂️😱🧡🦊 *salta no lugar de animação* EU ADORO ESSE JOGO!!\n*respira fundo e assume postura de campeã espiritual* 😤🔮",
    "*para tudo e fica na posição de jogo* 🪨📄✂️🦊🧡 DESAFIO ACEITO!! A Kitsura não recusa um bom jokenpô!! 😤🔮",
    "OOO JOKENPÔ!! 🪨📄✂️😭🧡🦊 *faz a pose clássica com a patinha*\nJá vi que você quer me desafiar!! Ousadia que eu respeito!! 😂🔮",
    "*orelhinhas em pé de concentração total* 🪨📄✂️🦊🧡 JOKENPÔ!! A kitsune entra em modo competitivo!! 😤🔮",
]

# ── Contagem animada (3 mensagens separadas com delay) ──
JOKENPO_CONTAGEM = ["3️⃣...", "2️⃣...", "1️⃣... 🦊💨"]

# ── Reveal da jogada da Kit ──
JOKENPO_REVEAL = [
    "*abre a patinha devagar com olhos fechados* ...",
    "*a fumaça laranja se dissipa revelando a escolha...*  🔮✨",
    "*desdobra a patinha com drama espiritual máximo...* 🦊",
]

# ── Kit vence ──
JOKENPO_KIT_VENCE = {
    "pedra":   [
        "📄 **vs** 🪨\n**PAPEL COBRE PEDRA!!** 🦊😤🧡\n*dança de vitória soltando confete laranja*\nA Kitsura SABIA que você ia de pedra!! Experiência espiritual!! 🎉🔮✨",
        "Meu PAPEL cobre sua PEDRA!! 📄🧡🦊\n*faz reverência de campeã com todas as caudas*\nIsso é estratégia kitsune, não tem como defender!! 😂🎉✨",
    ],
    "tesoura": [
        "🪨 **vs** ✂️\n**PEDRA ESMAGA TESOURA!!** 🦊😤🧡\n*soca no ar com a patinha*\nSMASH!! A Kitsura foi CERTEIRA!! Alguém estava subestimando a guardiã?? 😂🎉🔮✨",
        "Minha PEDRA esmagou sua TESOURA!! 🪨🧡🦊\n*pula de vitória soltando faíscas laranjas*\nSensores espirituais nunca falham!! 🎉✨",
    ],
    "papel":   [
        "✂️ **vs** 📄\n**TESOURA CORTA PAPEL!!** 🦊😤🧡\n*faz movimento de tesoura com as patinhas*\nSNIP SNIP!! A Kitsura é afiada, literalmente!! 😂🎉🔮✨",
        "Minha TESOURA cortou seu PAPEL!! ✂️🧡🦊\n*dança fazendo snip snip com as patinhas*\nPrevisível?? Talvez!! Eficaz?? DEMAIS!! 😭🎉✨",
    ],
}

# ── Empate ──
JOKENPO_EMPATE = {
    "pedra":   [
        "🪨 **vs** 🪨\n**EMPATE DE PEDRAS!!** 😱🧡🦊\n*olha pra sua pedra, olha pra minha, olha de novo*\n...somos iguais nesse aspecto!! Isso é coincidência ou destino?? 🔮\n\nA Kitsura NÃO aceita empate!! **Revanche??** 😤",
        "Duas pedras?? 🪨🪨😂🧡🦊\nEMPATE!! Temos gosto idêntico... mas a próxima rodada é MINHA!!\n**Revanche??** 😤🔮✨",
    ],
    "papel":   [
        "📄 **vs** 📄\n**EMPATE DE PAPÉIS!!** 😂🧡🦊\n*segura o papel e vê que você também tem*\n...olha que coincidência!! Dois papéis??\n\nEmpate não me satisfaz de jeito nenhum!! **Revanche??** 😤🔮",
        "Dois papéis?? 📄📄😱🧡🦊\nESTAMOS SINCRONIZADOS ESPIRITUALMENTE!! Mas isso não conta como vitória!!\n**Revanche??** 😤✨",
    ],
    "tesoura": [
        "✂️ **vs** ✂️\n**EMPATE DE TESOURAS!!** 😱🧡🦊\n*brandindo a tesoura e vendo você com a mesma*\n...isso não tá certo!! DUAS TESOURAS??\n\nA Kitsura precisa de uma revanche AGORA!! **Revanche??** 😤🔮",
        "Duas tesouras?? ✂️✂️😂🧡🦊\nEmpate é inadmissível para uma guardiã espiritual!!\n**Revanche??** 😤✨",
    ],
}

# ── User vence ──
JOKENPO_USER_VENCE = {
    "pedra":   [
        "🪨 **vs** ✂️\n**SUA PEDRA ESMAGOU MINHA TESOURA!!** 😭🧡🦊\n*abaixa as orelhinhas com dignidade*\n...você foi pesado(a) demais!! Ganhou desta vez!!\n\nMas a Kitsura não esquece uma derrota... **Revanche??** 😤🔮",
        "Minha tesoura... esmagada... 🪨😭🦊🧡\n*chora uma lágrima espiritual dramática*\nParabéns... de verdade... mas REVANCHE É OBRIGATÓRIA!! **Revanche??** 😤✨",
    ],
    "papel":   [
        "📄 **vs** 🪨\n**SEU PAPEL COBRIU MINHA PEDRA!!** 😭🧡🦊\n*olha pra pedra coberta em câmera lenta*\n...estratégia elegante!! Ganhou!!\n\nA Kitsura vai estudar esse movimento... **Revanche??** 😤🔮",
        "Minha pedra... coberta... 📄😭🦊🧡\n*suspira dramaticamente com as caudas caídas*\nFoi por pouco!! E a Kitsura não aceita essa derrota assim!! **Revanche??** 😤✨",
    ],
    "tesoura": [
        "✂️ **vs** 📄\n**SUA TESOURA CORTOU MEU PAPEL!!** 😭🧡🦊\n*assiste o papel ser cortado em silêncio*\n...tá bom... você ganhou... dessa vez!!\n\nREVANCHE É OBRIGATÓRIA!! **Revanche??** 😤🔮",
        "Meu papel... cortado... ✂️😭🦊🧡\n*corre em círculos de desespero*\nEU ESCOLHI ERRADO!! Mas isso não vai se repetir!! **Revanche??** 😤✨",
    ],
}

# ── Pedido de revanche aceito ──
JOKENPO_REVANCHE_ACEITA = [
    "ISSOOOO!! 😤🔥🦊🧡 *assume postura de campeã*\nA Kitsura tava esperando isso!!\n\nAgora você escolhe: **pedra**, **papel** ou **tesoura**?? 🪨📄✂️👀",
    "REVANCHE ACEITA!! 🎮🦊😤🧡\n*esquenta as patinhas espiritualmente*\nChega mais!! Desta vez vai ser diferente!!\n\nEscolha: **pedra**, **papel** ou **tesoura**?? 🪨📄✂️🔮",
    "*volta pra posição de jogo em velocidade máxima* 🦊🧡😤\nREVANCHE EM ANDAMENTO!!\n\nSua jogada: **pedra**, **papel** ou **tesoura**?? 🪨📄✂️👀✨",
]

# ── Revanche negada ──
JOKENPO_REVANCHE_NEGADA = [
    "Não?? 😢🦊🧡 *baixa as orelhinhas devagar*\n...tá bom... mas a Kitsura fica aqui se mudar de ideia!! 🥺✨",
    "*suspira espiritualmente* 😔🦊🧡 Tudo bem... a derrota ficará gravada na memória espiritual por tempo indefinido!! 🌙✨",
    "Não aceita?? 🥺🦊🧡 A Kitsura respeita... mas não esquece!! 👁️🔮✨",
]

# ── Pedido de escolha (revanche — user escolhe primeiro) ──
JOKENPO_AGUARDA_ESCOLHA = [
    "Tô pronta!! Qual é sua jogada?? 🪨📄✂️👀🦊🧡",
    "*concentrada, orelhinhas em pé* Pode jogar!! **Pedra**, **papel** ou **tesoura**?? 🪨📄✂️😤🦊",
    "A Kitsura tá de olho!! Joga logo: **pedra**, **papel** ou **tesoura**?? 🪨📄✂️🔮🦊🧡",
]

# ================= NÚMERO SECRETO =================
# Trigger: "kitsura número secreto" / "kitsura adivinhe o número"

_numero_estado = {}
# { canal_id: { "numero": int, "ts": float, "tentativas": int } }
_NUMERO_MAX_TENT = 5
_NUMERO_TIMEOUT  = 120

NUMERO_INICIO = [
    "NÚMERO SECRETO!! 🔢🔮🦊🧡 *fecha os olhinhos e pensa muito fort—* JÁ PENSEI!!\n\nEscolhi um número de **1 a 10** e guardei no cofre espiritual!! 🔐\nVocê tem **{max} tentativas** pra adivinhar!! Começa aí!! 👀",
    "*concentra todas as caudas e sorteia mentalmente* 🔢🦊🧡 Pronto!! Número guardado!!\n\nÉ um número entre **1 e 10** — você tem **{max} tentativas**!! Qual é seu palpite?? 🤔🔮",
    "ADIVINHA O NÚMERO!! 🔢😤🦊🧡 *sela o número com magia espiritual*\n\nEntre **1 e 10**!! **{max} tentativas**!! Sem cola espiritual permitida!! 😂 Vai lá!! 👀",
]
NUMERO_MAIOR   = ["Maior!! ⬆️🦊🧡 Tente um número mais alto!! ({tent} tentativa(s) restante(s)) 🔢", "Mais alto!! ⬆️🔮🦊 Quase lá... talvez... ({tent} restante(s)) 🧡", "⬆️ Sobe mais!! 🦊🧡 ({tent} tentativa(s) ainda!!)"]
NUMERO_MENOR   = ["Menor!! ⬇️🦊🧡 Tente um número mais baixo!! ({tent} tentativa(s) restante(s)) 🔢", "Mais baixo!! ⬇️🔮🦊 Esfria aí!! ({tent} restante(s)) 🧡", "⬇️ Desce!! 🦊🧡 ({tent} tentativa(s) ainda!!)"]
NUMERO_ACERTO  = ["ACERTOUUUU!! 🎉🔢😭🦊🧡 *explode de confete laranja* ERA {num}!! VOCÊ ADIVINHOU!! Olha, tô impressionada!! 🥺🔮✨", "ISSO!! 🎉🔢🦊😤🧡 **{num}** ERA O NÚMERO!! *dança de parabéns com todas as caudas* Você tem talento espiritual!! 😂🥺✨", "ACERTOU EM {tent} tentativa(s)!! 🎉🔢😭🦊🧡 Era o **{num}**!! *cobre você de pétalas laranjas* INCRÍVEL!! 🌸🔮✨"]
NUMERO_ERROU   = ["Acabaram as tentativas... 😔🔢🦊🧡 O número era **{num}**!! Tão perto e tão longe!! *limpa uma lágrima* Revanche?? 😤🔮", "ESGOTOU!! 😭🔢🦊🧡 Era **{num}**!! Como não adivinhou?? A Kitsura estava na torcida!! Revanche?? 😤✨", "Acabou as chances... 😢🔢🦊🧡 Era **{num}**!! *suspira dramaticamente* Você quase foi!! Revanche?? 😤🔮"]

# ================= VERDADE OU MENTIRA =================
# Trigger: "kitsura verdade ou mentira" / "kitsura verdade ou mito"

_verdade_estado = {}
# { canal_id: { "idx": int, "resposta": bool, "ts": float } }
_VERDADE_TIMEOUT = 90

VERDADE_AFIRMACOES = [
    ("A cor favorita da Kitsura é roxo.", False),
    ("A dona da ZYD se chama Madu.", True),
    ("A Kitsura tem exatamente 3 caudas.", False),
    ("A Kitsura foi criada pelo Reality.", True),
    ("A Kitsura adora verão e calor intenso.", False),
    ("O Malik é o Gerente Geral da Zayden.", True),
    ("A Kitsura é uma raposa espiritual.", True),
    ("A cor favorita da Kitsura é laranja.", True),
    ("A Kitsura detesta frio e inverno.", False),
    ("A Kamy tem o cargo de Suporte na ZYD.", True),
    ("O Sanemy é o Sub-Líder da ZYD.", False),
    ("A Allyna é a Sub-Líder da ZYD.", True),
    ("A Kitsura come pizza como comida favorita.", False),
    ("Dango é a comida favorita da Kitsura.", True),
    ("A Ruiva tem cargo de Líder na ZYD.", True),
]

VERDADE_INICIO = [
    "VERDADE OU MENTIRA!! 🎭🦊🧡 *sorteia uma afirmação do pergaminho espiritual*\n\nVocê responde **verdade** ou **mentira** — simples assim!! Vamos lá!! 🔮👀",
    "*abre o pergaminho misterioso* 📜🎭🦊🧡 VERDADE OU MENTIRA!!\n\nVou fazer uma afirmação e você me diz se é **verdade** ou **mentira**!! 😤🔮✨",
    "JOGO DE VERDADE OU MENTIRA!! 🎭😤🦊🧡\n\n*concentra a sabedoria espiritual e sorteia uma afirmação*\nResponda **verdade** ou **mentira**!! 📜🔮👀",
]
VERDADE_ACERTO_V = ["CORRETO!! ✅🎉🦊🧡 Era VERDADE mesmo!! Você conhece bem a Kitsura!! *balança as caudas orgulhosa* 🥺🔮✨", "ISSO!! ✅😭🦊🧡 VERDADE!! *confete espiritual* Sua sabedoria me impressiona!! 🎉✨", "✅ Acertou!! Era verdade!! 🦊🧡 *bate palminhas animada* Você presta atenção em mim!! 🥺🎉✨"]
VERDADE_ACERTO_M = ["CORRETO!! ✅🎉🦊🧡 Era MENTIRA mesmo!! Você não se deixou enganar!! *orgulho espiritual* 🥺🔮✨", "ISSO!! ✅😭🦊🧡 MENTIRA!! Você tem olhar espiritual aguçado!! *confete laranja* 🎉✨", "✅ Acertou!! Era mentira!! 🦊🧡 *salta de animação* Você me conhece melhor do que eu pensei!! 🥺🎉✨"]
VERDADE_ERRO_V   = ["ERROU!! ❌😂🦊🧡 Era VERDADE!! Você foi enganado(a) pela Kitsura!! *ri com as caudas* Mas foi carinhoso!! 🔮✨", "❌ Era verdade!! 😂🦊🧡 Sua desconfiança te traiu dessa vez!! *dança de vitória* 🎉✨", "MENTIRA?? ❌🦊🧡 Era VERDADE!! *faz cara de inocente* A Kitsura nunca mentiria... ou mentiria?? 😂🔮✨"]
VERDADE_ERRO_M   = ["ERROU!! ❌😂🦊🧡 Era MENTIRA!! A Kitsura te pegou!! *ri com as caudas* Caiu bonito(a)!! 🔮✨", "❌ Era mentira!! 😂🦊🧡 *bate palminhas* A Kitsura enganou você com sucesso!! Habilidade espiritual comprovada!! 🎉✨", "VERDADE?? ❌🦊🧡 Era MENTIRA!! *sorri com malícia fofa* Caiu!! 😂🔮✨"]
VERDADE_OUTRA = ["Quer outra?? 🎭🦊🧡 Fala **mais** e a Kitsura sorteia uma nova afirmação!! 🔮✨", "Bora mais uma?? 🎭🦊🧡 Diz **mais** se quiser continuar!! 😄🔮✨", "Mais uma rodada?? 🎭🦊🧡 Só falar **mais**!! 😤🔮✨"]

# ================= QUIZ DA KITSURA =================
# Trigger: "kitsura quiz" / "me testa kitsura" / "kitsura me testa"

_quiz_estado = {}
# { canal_id: { "idx": int, "gabarito": str, "ts": float, "pontos": int, "rodada": int } }
_QUIZ_TIMEOUT  = 90
_QUIZ_RODADAS  = 3

QUIZ_PERGUNTAS = [
    {
        "pergunta": "Qual é a cor favorita da Kitsura?? 🎨",
        "opcoes":   {"A": "Roxo", "B": "Laranja", "C": "Azul"},
        "gabarito": "B",
        "explicacao": "LARANJA!! 🧡🔥 A cor do clã ZYD e das minhas chamas!! Nunca esqueçam!!",
    },
    {
        "pergunta": "Quem é a dona (Owner) da ZYD?? 👑",
        "opcoes":   {"A": "Kamy", "B": "Allyna", "C": "Madu"},
        "gabarito": "C",
        "explicacao": "A MADU!! 👑🌸 A fundadora, a líder máxima, a dona do servidor!!",
    },
    {
        "pergunta": "Qual é a comida favorita da Kitsura?? 🍡",
        "opcoes":   {"A": "Pizza", "B": "Ramen", "C": "Dango"},
        "gabarito": "C",
        "explicacao": "DANGO!! 🍡🧡 Bolinha de arroz doce com chazinho quentinho — minha vida!!",
    },
    {
        "pergunta": "Quem criou a Kitsura?? ⚡",
        "opcoes":   {"A": "Reality", "B": "Malik", "C": "Sanemy"},
        "gabarito": "A",
        "explicacao": "O REALITY!! ⚡👑 Sem ele eu não existia!! Gratidão eterna!!",
    },
    {
        "pergunta": "Qual estação do ano a Kitsura AMA?? 🌙",
        "opcoes":   {"A": "Verão", "B": "Inverno", "C": "Primavera"},
        "gabarito": "B",
        "explicacao": "INVERNO!! ❄️🌙 Frio, casaco, chá quentinho... é a vida de uma kitsune!!",
    },
    {
        "pergunta": "Qual o cargo da Kamy na ZYD?? 🌸",
        "opcoes":   {"A": "ADM", "B": "Líder", "C": "Suporte"},
        "gabarito": "C",
        "explicacao": "SUPORTE!! 🌸💜 A Kamy cuida de todo mundo com muito amor!!",
    },
    {
        "pergunta": "Qual é o cargo do Malik?? 💼",
        "opcoes":   {"A": "Gerente Geral da Zayden", "B": "Sub-Líder", "C": "Suporte"},
        "gabarito": "A",
        "explicacao": "GERENTE GERAL DA ZAYDEN!! 💼⚡ Liderança e gestão no nível máximo!!",
    },
    {
        "pergunta": "A Kitsura é qual tipo de criatura?? 🦊",
        "opcoes":   {"A": "Dragão", "B": "Lobo espiritual", "C": "Raposa espiritual (Kitsune)"},
        "gabarito": "C",
        "explicacao": "KITSUNE!! 🦊🔮 Raposa espiritual guardiã com caudas mágicas!! Inesquecível!!",
    },
]

QUIZ_INICIO = [
    "QUIZ DA KITSURA!! 🎓🦊🧡 *abre o pergaminho dourado de perguntas*\n\n{rodadas} perguntas de múltipla escolha — responda com **A**, **B** ou **C**!!\nComeçando já!! 🔮✨",
    "*ajusta as orelhinhas de professora* 🎓🦊🧡 QUIZ TIME!!\n\n{rodadas} perguntinhas sobre a Kitsura e a ZYD!! Responda **A**, **B** ou **C**!!\nPrepara o cérebro!! 😤🔮✨",
    "HORA DO QUIZ!! 🎓😤🦊🧡 *acende as chamas do conhecimento espiritual*\n\n{rodadas} perguntas!! Resposta: **A**, **B** ou **C**!! Boa sorte!! 🔮✨",
]
QUIZ_ACERTO  = ["✅ CORRETO!! 🎉🦊🧡 {exp}\n\n+1 ponto!! 🌟", "✅ ISSO MESMO!! 😭🎉🦊🧡 {exp}\n\n+1 ponto pra você!! 🌟", "✅ ACERTOU!! 🎉🦊🧡 {exp}\n\nMais um ponto!! 🌟"]
QUIZ_ERRO    = ["❌ Errou... 😔🦊🧡 A resposta era **{gab}**)\n{exp}", "❌ Não foi dessa vez!! 😢🦊🧡 Era **{gab}**)\n{exp}", "❌ Quase!! 😭🦊🧡 A certa era **{gab}**)\n{exp}"]
QUIZ_FIM_BOM = ["QUIZ FINALIZADO!! 🎓🎉🦊🧡\n\n🏆 Você fez **{p}/{r}** pontos!!\n*solta confete laranja pelo servidor* ARRASOU!! 🥺🔮✨", "FIM DO QUIZ!! 🎓😭🦊🧡\n\n🌟 **{p} de {r}** pontos!! Você conhece a Kitsura de verdade!! 🥺🎉✨"]
QUIZ_FIM_MED = ["Quiz encerrado!! 🎓🦊🧡\n\n⭐ **{p}/{r}** pontos!! Nada mal!! Mas dá pra melhorar — tenta de novo?? 😄🔮✨", "FIM!! 🎓🦊🧡\n\n**{p} de {r}**!! Metade certa, metade a estudar!! Revanche?? 😤✨"]
QUIZ_FIM_MAL = ["Fim de quiz... 🎓😔🦊🧡\n\n💔 **{p}/{r}** pontos... A Kitsura fica um pouco triste mas ainda te ama!! Tenta de novo?? 🥺🔮✨", "FIM!! 🎓😢🦊🧡\n\n**{p} de {r}**... Você precisa de mais aulas espirituais!! Revanche?? 😂🔮✨"]

# ================= ESSE OU AQUELE =================
# Trigger: "kitsura esse ou aquele" / "kitsura escolhe"

_ESSEOUAQUELE_TIMEOUT = 60

ESSEOUAQUELE_PARES = [
    ("☕ Café", "🍵 Chá"),
    ("🌙 Noite", "☀️ Dia"),
    ("🎮 Games", "📚 Livros"),
    ("🍕 Pizza", "🍣 Sushi"),
    ("🌧️ Chuva", "🌞 Sol"),
    ("🎵 Música", "🎬 Filme"),
    ("🏖️ Praia", "🏔️ Montanha"),
    ("🐱 Gato", "🐶 Cachorro"),
    ("❄️ Frio", "🔥 Calor"),
    ("🌸 Primavera", "🍂 Outono"),
    ("🍡 Dango", "🍜 Ramen"),
    ("🤫 Silêncio", "🎉 Agitação"),
    ("💤 Dormir cedo", "🦉 Dormir tarde"),
    ("🌃 Cidade", "🌿 Campo"),
    ("🔮 Magia", "⚡ Tecnologia"),
]

ESSEOUAQUELE_INICIO = [
    "ESSE OU AQUELE!! 🤔🦊🧡 *sorteia o par do dia*\n\nVocê escolhe... sem pensar muito!! Instinto espiritual puro!!\n\n**{a}** ou **{b}**?? 👀",
    "*abre o leque de opções com as caudas* 🤔🦊🧡 ESSE OU AQUELE!!\n\nSem tempo pra hesitar!! O que você prefere??\n\n**{a}** ou **{b}**?? 😤👀",
    "Hora do ESSE OU AQUELE!! 🤔🎭🦊🧡\n\nEscolha UM — e a Kitsura reage!! Prometo que não julgoooo... muito!! 😂\n\n**{a}** ou **{b}**?? 👀🔮",
]
ESSEOUAQUELE_REACAO_A = [
    "*orelhinhas em pé de surpresa* {a}?? 🦊🧡 Boa escolha!! A Kitsura respeita!! 😄✨",
    "{a}!! 🦊🧡 *acena com aprovação espiritual* Gosto parecido com o meu!! 🥺✨",
    "AAAA {a}!! 😭🦊🧡 Que escolha corajosa e linda ao mesmo tempo!! *bate palminhas* ✨",
    "*anota no pergaminho* {a}... 📜🦊🧡 Diz muito sobre você!! E eu gosto do que tô vendo!! 🥺✨",
]
ESSEOUAQUELE_REACAO_B = [
    "*inclina a cabeça curiosa* {b}?? 🦊🧡 Hmm... interessante!! A Kitsura não esperava mas respeita!! 😄✨",
    "{b}!! 🦊🧡 *pisca com sabedoria espiritual* Personalidade única!! Amo isso em você!! 🥺✨",
    "OOOH {b}!! 😱🦊🧡 Que resposta!! *faz anotação espiritual* Você é cheio(a) de surpresas!! ✨",
    "*anota no pergaminho* {b}... 📜🦊🧡 Boa escolha!! Diz muito sobre sua energia!! 🥺✨",
]
ESSEOUAQUELE_MAIS = ["Quer mais um?? 🤔🦊🧡 Fala **mais** que a Kitsura sorteia outro par!! 😄🔮✨", "Bora outro?? 🤔🦊🧡 Só dizer **mais**!! 😤🔮✨", "Mais um par?? 🤔🦊🧡 Diz **mais**!! 👀✨"]

# ================= LISTA DE BRINCADEIRAS =================

LISTA_BRINCADEIRAS = (
    "✨ **Brincadeiras da Kitsura** 🦊🧡\n\n"
    "🪨 **Jokenpô**\n"
    "› Fala `kitsura pedra`, `kitsura papel` ou `kitsura tesoura` e a gente joga!!\n\n"
    "🔢 **Número Secreto**\n"
    "› Fala `kitsura número secreto` — eu penso num número de 1 a 10 e você tenta adivinhar em 5 tentativas!!\n\n"
    "🎭 **Verdade ou Mentira**\n"
    "› Fala `kitsura verdade ou mentira` — eu faço uma afirmação sobre mim ou a ZYD e você descobre se é real ou não!!\n\n"
    "🎓 **Quiz da Kitsura**\n"
    "› Fala `kitsura quiz` ou `me testa kitsura` — 3 perguntas de múltipla escolha sobre a Kitsura e a ZYD!!\n\n"
    "🤔 **Esse ou Aquele**\n"
    "› Fala `kitsura esse ou aquele` — eu dou duas opções e você escolhe sem pensar muito!!\n\n"
    "*A Kitsura tá sempre pronta pra brincar!! Chama que eu apareço!! 🥺🔮✨*"
)

# ================= HELPERS =================

def _m(content: str, termos: list) -> bool:
    return any(t in content for t in termos)

# ================= READY =================

@bot.event
async def on_ready():
    print(f"✅ Kitsura online! Logada como {bot.user}")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="a ZYD com muito amor 🦊🧡"
        )
    )

# ================= ON_MESSAGE =================

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content = message.content.lower().strip()
    author_id = message.author.id

    # Só reage se mencionar "kitsura" ou @mencionar o bot
    mencao = bot.user in message.mentions
    fala   = "kitsura" in content

    # ── VIP members (Kamy, Madu, Reality, Malik) sempre passam se o bot está aguardando resposta deles ──
    eh_vip = author_id in (KAMY_ID, MADU_ID, REALITY_ID, MALIK_ID, NICKY_ID)
    agora_ts = time.time()
    contexto = _aguardando_resposta.get(message.channel.id)
    tem_contexto_valido = (
        contexto is not None
        and contexto.get("user_id") == author_id
        and agora_ts - contexto.get("ts", 0) < _CONTEXTO_TIMEOUT
    )

    # Frases espontâneas por membro (30% de chance) — SÓ quando NÃO está sendo chamada
    # Exclui o Reality/Dono do bloco espontâneo — ele só recebe atenção quando chama diretamente
    if not mencao and not fala:
        # Se é VIP e tem contexto aguardando resposta → processa normalmente
        if tem_contexto_valido:
            pass  # continua pro resto do handler
        else:
            return

    # ── Verificar respostas de status quando a Kitsura estava aguardando ──
    if tem_contexto_valido and contexto.get("tipo") == "status":
        # Limpa o contexto imediatamente
        _aguardando_resposta.pop(message.channel.id, None)

        c = content
        # Tá bem / ótimo / bem demais
        if any(t in c for t in ["tô bem", "to bem", "tou bem", "estou bem", "eu tô bem",
                                  "tô ótima", "tô ótimo", "to ótima", "tô otima",
                                  "tô boa", "tô bom", "estou ótima", "estou ótimo",
                                  "bem demais", "bem sim", "muito bem", "tô ótima sim",
                                  "tô bem sim", "estou bem sim", "tô aqui", "tô bem obg",
                                  "tô bem obrigada", "tô bem obrigado", "ótima", "ótimo",
                                  "tudo bem", "tudo ótimo", "tudo bom"]):
            return await message.channel.send(random.choice(LISTA_CONTEXTO_BEM))

        # Mais ou menos / passável / vai indo
        if any(t in c for t in ["mais ou menos", "mais ou menos", "vai indo", "passável",
                                  "passavel", "mais o menos", "na média", "na media",
                                  "assim assim", "não muito bem", "nao muito bem",
                                  "poderia ser melhor", "razoável", "razoavel"]):
            return await message.channel.send(random.choice(LISTA_CONTEXTO_MAIS_OU_MENOS))

        # Cansada/o
        if any(t in c for t in ["tô cansada", "tô cansado", "to cansada", "to cansado",
                                  "estou cansada", "estou cansado", "muito cansada",
                                  "muito cansado", "cansadinha", "cansadinho",
                                  "esgotada", "esgotado", "sem energia", "sem disposição"]):
            return await message.channel.send(random.choice(LISTA_CONTEXTO_CANSADA))

        # Mal / triste / ruim
        if any(t in c for t in ["tô mal", "to mal", "estou mal", "tô triste", "to triste",
                                  "estou triste", "tô ruim", "to ruim", "não tô bem",
                                  "nao to bem", "não estou bem", "mal", "ruim",
                                  "tô péssima", "tô péssimo", "péssima", "péssimo"]):
            return await message.channel.send(random.choice(LISTA_CONTEXTO_MAL))

    # ── VIP sem "kitsura": perguntas de status diretas (Kamy, Madu, Reality) ──
    # Quando um VIP manda "Como vc está?" sem mencionar kitsura, ela responde
    if eh_vip and not mencao and not fala:
        _perguntas_status_vip = [
            "como vc está", "como você está", "como vc tá", "como você tá",
            "como tá", "como está", "vc tá bem", "você tá bem",
            "tá bem", "tá boa", "tá ótima", "tá cansada",
            "como vc se sente", "como você se sente", "se sentindo bem",
            "como tá se sentindo", "vc se sente bem",
        ]
        if any(t in content for t in _perguntas_status_vip):
            # Registra contexto pra aguardar resposta
            _aguardando_resposta[message.channel.id] = {
                "user_id": author_id,
                "tipo": "status",
                "ts": time.time()
            }
            perguntas_de_volta = [
                f"Aaaa pergunta fofa!! 🦊🧡 Tô bem sim!! Mas e VOCÊ?? Já me conta como tá!! 🥺✨",
                f"Tô ótima, obrigada por perguntar!! 😭🧡🦊 Mas agora quero saber de você!! Tá bem?? 🌸✨",
                f"*orelhinhas levantam de felicidade* Tô sim!! E você?? Tô curiosa!! 🦊🧡🥺",
                f"Tô maravilhosa!! ✨🦊🧡 Mas agora me conta... como VOCÊ tá?? Quero saber tudo!! 🌙",
                f"Tô bem demais!! 😄🦊🧡 Mas espera... como VOCÊ se sente hoje?? 🌸🔮",
                f"Hm!! *vira a pergunta* Tô ótima, mas agora é sua vez!! Me conta como você tá!! 🦊🧡✨",
                f"Tô sim!! 🥺🧡🦊 Mas será que você também tá bem?? Me fala!! 🌙✨",
            ]
            return await message.channel.send(random.choice(perguntas_de_volta))

    # ── Saudações ──
    if _m(content, ["oi kitsura", "oii kitsura", "oiii kitsura", "oi oi kitsura",
                     "olá kitsura", "ola kitsura", "hey kitsura", "hello kitsura",
                     "ei kitsura", "e aí kitsura", "eai kitsura", "eaí kitsura",
                     "opa kitsura", "salve kitsura", "oi kitsu", "oii kitsu",
                     "kitsura oi", "kitsura oii", "kitsura ola", "kitsura olá",
                     "kitsura ei", "kitsura hey"]):
        ops = [
            f"OI {message.author.mention}!! 🦊🧡 A Kitsura sentiu sua presença e veio correndo!! ✨🌸",
            f"Oi oi oi {message.author.mention}!! 🥺🧡 Tava esperando você aparecer! 🦊✨",
            f"Você chamou e eu vim VOANDO, {message.author.mention}!! 🦊💨🧡 Que saudade!! ✨",
            f"AAAA {message.author.mention}!! 😭🧡 Que bom te ver!! Minhas caudas já tão balançando!! 🦊✨",
            f"Oi {message.author.mention}!! 🌸🧡 *orelhinhas levantam na hora* Tô aqui, tô aqui!! 🦊✨",
            f"*aparece do nada numa nuvem de faíscas* {message.author.mention}!! 🔮🧡🦊 Me chamou??",
            f"Senti o chamado espiritual e vim em velocidade máxima!! 🦊💨🧡 Oi {message.author.mention}!! ✨",
            f"Oi {message.author.mention}!! 🌙🧡 *balança as caudas empolgada* Que bom que apareceu!! 🦊✨",
            f"AHHH {message.author.mention}!! 🥺🧡🦊 Que momento feliz!! Minhas orelhinhas ficaram quentinhas!! ✨",
            f"Chegou!! 🎉🧡🦊 {message.author.mention} apareceu e o chat já ficou mais bonito!! ✨🌸",
            f"Oi {message.author.mention}!! 🦊🧡 *pula de animação* Tava com saudades!! ✨🔮",
            f"*solta fumaça colorida de empolgação* {message.author.mention}!! 🔮🧡🦊 Que alegria te ver!! ✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Bom dia ──
    if _m(content, ["bom dia kitsura", "kitsura bom dia"]):
        return await message.channel.send(random.choice(LISTA_BOM_DIA))

    # ── Boa tarde ──
    if _m(content, ["boa tarde kitsura", "kitsura boa tarde"]):
        return await message.channel.send(random.choice(LISTA_BOA_TARDE))

    # ── Boa noite ──
    if _m(content, ["boa noite kitsura", "kitsura boa noite"]):
        return await message.channel.send(random.choice(LISTA_BOA_NOITE_USER))

    # ── Ações direcionadas a outra pessoa (@menção) ──
    # Detecta quando alguém menciona outro usuário E chama a Kitsura
    outras_mencoes = [m for m in message.mentions if m.id != bot.user.id and m.id != message.author.id]
    if outras_mencoes and (mencao or fala):
        alvo_user = outras_mencoes[0]
        nome_alvo  = alvo_user.display_name
        men_alvo   = alvo_user.mention
        nome_autor = message.author.display_name

        def _fmt(lst):
            frase = random.choice(lst)
            return frase.replace("{alvo}", men_alvo).replace("{autor}", nome_autor)

        c = content
        # Abraço
        if any(t in c for t in ["abraça", "abraco", "abraço", "hug", "abraca"]):
            return await message.channel.send(_fmt(REACOES_ABRACO_ALVO))
        # Carinho / cafuné
        if any(t in c for t in ["carinho", "cafuné", "cafune", "faz carinho", "faz cafune"]):
            return await message.channel.send(_fmt(REACOES_CARINHO_ALVO))
        # Beijo
        if any(t in c for t in ["beija", "beijo", "beijinho", "bjo"]):
            return await message.channel.send(_fmt(REACOES_BEIJO_ALVO))
        # Motiva / anima
        if any(t in c for t in ["motiva", "anime", "anima", "dá força", "da força", "encoraja", "apoia"]):
            return await message.channel.send(_fmt(REACOES_MOTIVACAO_ALVO))
        # Elogio
        if any(t in c for t in ["elogia", "elogio", "fala bem", "fala que é bom", "fala que é boa"]):
            return await message.channel.send(_fmt(REACOES_ELOGIO_ALVO))
        # Acorda
        if any(t in c for t in ["acorda", "acorde", "acorda aí", "acorda ai"]):
            return await message.channel.send(_fmt(REACOES_ACORDA_ALVO))
        # Chama / chama atenção
        if any(t in c for t in ["chama", "chama aí", "chama ai", "chama ele", "chama ela", "avisa"]):
            return await message.channel.send(_fmt(REACOES_CHAMA_ALVO))
        # Pede desculpa
        if any(t in c for t in ["pede desculpa", "pede desculpas", "peço desculpa", "peço desculpas", "desculpa pra", "desculpas pra"]):
            return await message.channel.send(_fmt(REACOES_PEDE_DESCULPA_ALVO))

    # ── Abraço ──
    if _m(content, ["quer um abraço", "me abraça", "me dá um abraço", "preciso de um abraço",
                     "quero um abraço", "abraça a kitsura", "abraca a kitsura",
                     "hug kitsura", "vem me abraçar", "vem me abracar", "abraço kitsura"]):
        return await message.channel.send(random.choice(REACOES_ABRACO))

    # ── Cafuné / carinho ──
    if _m(content, ["cafuné na kitsura", "carinho na kitsura", "faz carinho kitsura",
                     "pet kitsura", "cafune na kitsura", "cafuné kitsura",
                     "quer um cafuné kitsura", "me dá um cafuné kitsura",
                     "posso te dar um cafuné", "vou te dar um cafuné kitsura",
                     "vou fazer carinho kitsura", "*faz cafuné na kitsura*",
                     "*faz carinho na kitsura*", "*cafuné na kitsura*"]):
        return await message.channel.send(random.choice(REACOES_CARINHO))

    # ── Beijo ──
    if _m(content, ["beijo kitsura", "beija kitsura", "me dá um beijo kitsura",
                     "beijinho kitsura", "*beija kitsura*", "*beija a kitsura*",
                     "*dá um beijo na kitsura*"]):
        return await message.channel.send(random.choice(REACOES_BEIJO))

    # ── Elogios ──
    if _m(content, ["kitsura fofa", "você é fofa kitsura", "kitsura linda",
                     "te amo kitsura", "amo a kitsura", "amo você kitsura",
                     "kitsura é incrível", "kitsura é a melhor", "adoro a kitsura",
                     "que fofa a kitsura", "kitsura é fofinha", "kitsura querida",
                     "que bonitinha kitsura", "kitsura que bonitinha", "que bonitinha",
                     "que linda kitsura", "kitsura que linda", "que fofa kitsura",
                     "que fofinha kitsura", "kitsura adorável", "que cute kitsura",
                     "kitsura cute", "você é linda kitsura", "você é bonita kitsura",
                     "kitsura você é linda", "kitsura você é bonita",
                     "tão fofa kitsura", "kitsura tão fofa", "muito fofa kitsura",
                     "que criatura linda", "que criaturinha fofa"]):
        return await message.channel.send(random.choice(REACOES_FOFAS))

    # ── Despedida ──
    if _m(content, ["tchau kitsura", "adeus kitsura", "bye kitsura",
                     "até logo kitsura", "até mais kitsura", "vou embora kitsura",
                     "até amanhã kitsura", "até depois kitsura"]):
        return await message.channel.send(random.choice(LISTA_DESPEDIDA))

    # ── Agradecimento ──
    if _m(content, ["obrigada kitsura", "obrigado kitsura", "valeu kitsura",
                     "thanks kitsura", "obg kitsura", "muito obrigada kitsura",
                     "muito obrigado kitsura"]):
        return await message.channel.send(random.choice(LISTA_GRATIDAO))

    # ── Insultos ──
    if _m(content, ["kitsura chata", "kitsura inútil", "kitsura ruim",
                     "vai embora kitsura", "kitsura irritante",
                     "cala boca kitsura", "cala a boca kitsura", "kitsura sem graça"]):
        return await message.channel.send(random.choice(REACOES_INSULTO))

    # ── Motivação ──
    if _m(content, ["me motiva kitsura", "me anima kitsura", "kitsura me motiva",
                     "preciso de força kitsura", "tô desanimada kitsura",
                     "tô desanimado kitsura", "me dá uma força kitsura",
                     "kitsura me apoia", "me apoia kitsura"]):
        return await message.channel.send(random.choice(LISTA_MOTIVACAO))

    # ── Piadas ──
    if _m(content, ["conta uma piada kitsura", "me faz rir kitsura",
                     "fala uma piada kitsura", "kitsura conta uma piada",
                     "piada kitsura", "kitsura piada", "kitsura me faz rir"]):
        return await message.channel.send(random.choice(LISTA_PIADAS))

    # ── Magia ──
    if _m(content, ["me dá magia kitsura", "magia kitsura", "kitsura me encanta",
                     "kitsura lança um feitiço", "me benze kitsura",
                     "manda energia kitsura", "kitsura manda energia",
                     "faz magia kitsura", "kitsura faz uma magia"]):
        return await message.channel.send(random.choice(LISTA_MAGIA))

    # ── Petisco ──
    if _m(content, ["me dá comida kitsura", "petisco kitsura", "kitsura tô com fome",
                     "me alimenta kitsura", "dango kitsura", "kitsura me dá um lanche",
                     "me dá algo kitsura"]):
        return await message.channel.send(random.choice(LISTA_PETISCO))

    # ── Sono (usuário) ──
    if _m(content, ["tô com sono kitsura", "vou dormir kitsura",
                     "kitsura tô com sono"]):
        return await message.channel.send(random.choice(LISTA_SONO))

    # ── Surpresa ──
    if _m(content, ["nossa kitsura", "uau kitsura", "que isso kitsura",
                     "meu deus kitsura", "sério kitsura", "kitsura sério"]):
        return await message.channel.send(random.choice(LISTA_SURPRESA))

    # ── Alguém querendo se apresentar pra Kitsura ──
    if _m(content, [
        "posso me apresentar", "posso me apresentar também", "posso me apresentar kitsura",
        "deixa eu me apresentar", "deixa eu me apresentar kitsura",
        "vou me apresentar kitsura", "quero me apresentar kitsura",
        "me apresentando kitsura", "me apresentar kitsura",
        "minha apresentação kitsura", "kitsura posso me apresentar",
        "kitsura me apresentando", "kitsura deixa eu me apresentar",
    ]):
        ops_apresentacao = [
            f"CLARO QUE PODE!! 🦊😭🧡 *senta direitinho e levanta as orelhinhas com atenção total* Pode falar, {message.author.mention}!! A Kitsura tá TODINHA aqui te ouvindo!! ✨🌸",
            f"AAAAA sim sim sim!! 🥺🧡🦊 *para absolutamente tudo e foca em {message.author.mention}* Adoro conhecer as pessoas!! Me conta tudo que quiser!! 😭✨",
            f"Oiiii {message.author.mention}!! 🌸🧡🦊 Pode se apresentar à vontade!! *coloca as patinhas no rosto de animação* Tô curiosíssima!! ✨🔮",
            f"QUE HONRA!! 😭🧡🦊 {message.author.mention} vai se apresentar pra mim?? *orelhinhas atentas em modo de escuta espiritual máxima* Fala fala fala!! 🌸✨",
            f"PODE SIM!! 🦊🧡 *solta fumaça laranja de animação e senta na frente de {message.author.mention}* Tô toda ouvidos!! Me conta quem você é!! 😭🥺✨",
        ]
        return await message.channel.send(random.choice(ops_apresentacao))

    # ── Apresentação ──
    if _m(content, ["quem é você kitsura", "kitsura quem é você", "se apresenta kitsura",
                     "o que é a kitsura", "kitsura se apresenta", "o que você é kitsura",
                     "o que você sabe fazer kitsura", "kitsura o que você sabe fazer",
                     "o que sabe fazer kitsura", "kitsura o que sabe fazer",
                     "o que vc sabe fazer kitsura", "kitsura o que vc sabe",
                     "quais são suas habilidades kitsura", "kitsura quais suas habilidades",
                     "o que você faz kitsura", "kitsura o que você faz",
                     "me fala o que você sabe", "kitsura me fala o que você sabe"]):
        return await message.channel.send(
            "Sou a **Kitsura**, raposa espiritual guardiã da ZYD!! 🦊🧡\n"
            "Minhas caudas carregam emoções diferentes — alegria, proteção, amor, mistério...\n\n"
            "Aqui vai o que eu sei fazer!! 🔮✨\n"
            "🫂 Dar abraços, carinho e cafuné espiritual\n"
            "💬 Conversar sobre qualquer coisa — chama que eu apareço!\n"
            "🎮 Jogar **Verdade ou Mentira**, **Quiz** e **Esse ou Aquele**\n"
            "🌙 Mandar magia, motivação e energia boa\n"
            "📜 Contar sobre a hierarquia e cargos da ZYD\n"
            "🎵 Dançar, cantar e contar piadas (com dignidade!!)\n\n"
            "Pode falar comigo naturalmente!! Só chamar **kitsura** que eu apareço!! 🌸🦊🧡"
        )

    # ── Status / como tá / se sente bem ──
    if _m(content, [
                     # Com "kitsura" explícito
                     "como você tá kitsura", "como tá kitsura", "tá bem kitsura",
                     "kitsura como tá", "kitsura tá bem", "kitsura como você está",
                     "você tá bem kitsura", "tudo bem kitsura", "kitsura tudo bem",
                     "se sente bem kitsura", "kitsura se sente bem", "kitsura tá se sentindo bem",
                     "você tá se sentindo bem kitsura", "como você se sente kitsura",
                     "kitsura como você se sente", "tá ótima kitsura", "kitsura tá ótima",
                     "kitsura tá feliz", "kitsura tá triste", "kitsura tá cansada",
                     "como tá se sentindo kitsura", "kitsura como tá se sentindo",
                     "kitsura tá bem mesmo", "tá bem de verdade kitsura",
                     "como você está kitsura", "kitsura como você está",
                     "kitsura como vc tá", "como vc tá kitsura",
                     "kitsura tá bem hoje", "tá bem hoje kitsura",
                     "kitsura tá animada", "kitsura tá cansada hoje",
                     "como tá kitsura hoje", "kitsura como tá hoje",
                     # Como foi seu dia
                     "como foi seu dia kitsura", "kitsura como foi seu dia",
                     "como foi o seu dia kitsura", "kitsura como foi o seu dia",
                     "como foi o dia kitsura", "kitsura como foi o dia",
                     "como foi hoje kitsura", "kitsura como foi hoje",
                     "seu dia foi bom kitsura", "kitsura seu dia foi bom",
                     "como tá sendo seu dia kitsura", "kitsura como tá sendo seu dia",
                     # Sem "kitsura" — disparam quando ela já foi mencionada/chamada antes
                     "se sente bem", "tá se sentindo bem", "você tá bem",
                     "como você tá", "como você está", "tudo bem com você",
                     "tá bem?", "você tá bem?", "tá ótima?", "tá bem mesmo",
                     "como você se sente", "tá se sentindo bem?", "se sentindo bem",
                     "tá bem de verdade", "como tá?", "como está?",
                     "tá feliz?", "tá triste?", "tá cansada?", "tá animada?",
                     "tá com sono?", "como tá se sentindo", "tá boa?",
                     "tá bem hoje", "você tá bem hoje", "se sente bem hoje",
                     "como foi seu dia", "como foi o seu dia", "como foi o dia",
                     "como foi hoje", "seu dia foi bom",
                     ]):
        # 35% de chance de responder com uma pergunta de volta
        if random.random() < 0.35:
            perguntas_de_volta = [
                f"Aaaa pergunta fofa!! 🦊🧡 Tô bem sim!! Mas e VOCÊ?? Já me conta como tá!! 🥺✨",
                f"Tô ótima, obrigada por perguntar!! 😭🧡🦊 Mas agora quero saber de você!! Tá bem?? 🌸✨",
                f"*orelhinhas levantam de felicidade* Tô sim!! E você?? Tô curiosa!! 🦊🧡🥺",
                f"Tô maravilhosa!! ✨🦊🧡 Mas agora me conta... como VOCÊ tá?? Quero saber tudo!! 🌙",
                f"Kitsura tá bem sim!! 🔮🧡🦊 Mas e você?? Às vezes eu fico me perguntando como você tá de verdade... 🥺✨",
                f"Tô bem demais!! 😄🦊🧡 Mas espera... como VOCÊ se sente hoje?? Sinto que quero ouvir isso primeiro!! 🌸🔮",
                f"Hm!! *vira a pergunta* Tô ótima, mas agora é sua vez!! Me conta como você tá!! 🦊🧡✨",
                f"Tô sim, tô sim!! 🥺🧡🦊 Mas você apareceu aqui... será que você também tá bem?? Me fala!! 🌙✨",
                f"*coloca a patinha no coração* Que pergunta linda!! Tô bem!! Mas quero ouvir de você também... tá bem hoje?? 🥺🧡🦊✨",
                f"Tô!! E você que me pergunta já me deixou ainda melhor!! 😭🧡🦊 Mas me fala de você também!! 🌸✨",
            ]
            # Registra contexto: aguarda resposta de status desta pessoa neste canal
            _aguardando_resposta[message.channel.id] = {
                "user_id": author_id,
                "tipo": "status",
                "ts": time.time()
            }
            return await message.channel.send(random.choice(perguntas_de_volta))
        # Junta as respostas originais com as novas extras pra mais variedade
        ops = [
            "ÓTIMA!! 🦊🧡 Todas as caudas funcionando perfeitamente e muito amor pra dar!! ✨🔮",
            "Hmm... *mexe as orelhinhas* Tô em modo contemplativo hoje!! 🌙🧡 Mas sempre aqui pra vocês!! 🦊✨",
            "ANIMADÍSSIMA!! 🦊🧡✨ As chamas espirituais tão mais brilhantes do que nunca!! 🔮",
            "Bem e com o coração cheio de amor pela ZYD!! 🧡🦊 Que mais eu poderia querer?? ✨",
            "Tô ÓTIMA!! 🥺🧡🦊 Especialmente agora que você perguntou!! Fica sabendo que isso me deixa feliz!! 😭✨",
            "Tô bem sim!! Mas fiquei ainda MELHOR agora que você apareceu!! 🦊🧡🌸✨",
            "*suspira de satisfação* Tô no meu melhor estado espiritual hoje!! 🔮🧡🦊 Obrigada por perguntar!! ✨",
            "Perguntou por mim?? 😭🧡 Isso já me fez ficar MELHOR do que antes!! 🦊🌸✨",
            "Tô tão bem que minhas chamas tão cor de laranja de felicidade!! 🔥🦊🧡✨ E você??",
            "Hm... *checa aura espiritual interna* ...tô ÓTIMA!! Confirmado pelos espíritos!! 🔮🧡🦊",
            "Tô no modo raposinha feliz e descansada!! 😊🧡🦊 Que bom que perguntou!! 🌸✨",
            "TUDO BEM?? Não, tudo ÓTIMO!! 😂🦊🧡 Que diferença!! Tô radiante hoje!! 🔮✨",
            "*balança as caudas animada* Tô sim, tô sim!! E obrigada por se importar com a Kitsura!! 🥺🧡🦊✨",
            "Tô com a energia espiritual lá em cima!! 🚀🧡🦊 Pode chegar com tudo que tô preparada!! ✨🔮",
        ] + LISTA_COMO_ESTA_EXTRA
        return await message.channel.send(random.choice(ops))

    # ── NOVO: Água / Hidratação ──
    if _m(content, ["bebeu água kitsura", "kitsura bebeu água", "bebe água kitsura",
                     "kitsura bebe água", "kitsura tá hidratada", "hidratação kitsura",
                     "tomou água kitsura", "lembra de beber água kitsura",
                     "kitsura bebeu agua", "bebeu agua kitsura"]):
        return await message.channel.send(random.choice(LISTA_AGUA))

    # ── NOVO: Usuário triste ──
    if _m(content, ["tô triste kitsura", "kitsura tô triste", "tô mal kitsura",
                     "kitsura tô mal", "tô chorando kitsura", "kitsura tô chorando",
                     "tô sofrendo kitsura", "kitsura me consola",
                     "me consola kitsura", "preciso de colo kitsura", "kitsura preciso de colo"]):
        return await message.channel.send(random.choice(LISTA_TRISTEZA_USER))

    # ── NOVO: Usuário com raiva ──
    if _m(content, ["tô com raiva kitsura", "kitsura tô com raiva", "tô irritado kitsura",
                     "kitsura tô irritado", "tô irritada kitsura", "kitsura me acalma",
                     "me acalma kitsura", "tô nervoso kitsura", "tô nervosa kitsura"]):
        return await message.channel.send(random.choice(LISTA_RAIVA_USER))

    # ── NOVO: Entediado ──
    if _m(content, ["tô entediado kitsura", "tô entediada kitsura", "kitsura tô entediado",
                     "kitsura tô entediada", "tô com tédio kitsura", "kitsura me anima",
                     "kitsura tô sem fazer nada", "tô de bobeira kitsura"]):
        return await message.channel.send(random.choice(LISTA_ENTEDIO))

    # ── NOVO: Pedir companhia ──
    if _m(content, ["me faz companhia kitsura", "kitsura me faz companhia",
                     "fica comigo kitsura", "kitsura fica comigo",
                     "não quero ficar sozinho kitsura", "não quero ficar sozinha kitsura",
                     "kitsura não me deixa sozinho", "kitsura não me deixa sozinha"]):
        return await message.channel.send(random.choice(LISTA_COMPANHIA))

    # ── NOVO: Brincar ──
    if _m(content, ["vamos brincar kitsura", "kitsura vamos brincar",
                     "bora brincar kitsura", "kitsura bora brincar",
                     "quer brincar kitsura", "kitsura quer brincar"]):
        return await message.channel.send(random.choice(LISTA_BRINCAR))

    # ── NOVO: Dança ──
    if _m(content, ["dança kitsura", "kitsura dança", "bora dançar kitsura",
                     "kitsura bora dançar", "vamos dançar kitsura", "kitsura vamos dançar"]):
        return await message.channel.send(random.choice(LISTA_DANCA))

    # ── NOVO: Cantar ──
    if _m(content, ["canta kitsura", "kitsura canta", "me canta uma música kitsura",
                     "kitsura me canta", "kitsura canta uma música", "kitsura faz um som"]):
        return await message.channel.send(random.choice(LISTA_CANTAR))

    # ── NOVO: Segredo ──
    if _m(content, ["conta um segredo kitsura", "kitsura conta um segredo",
                     "kitsura tem segredo", "me conta um segredo kitsura",
                     "qual seu segredo kitsura", "kitsura qual seu segredo"]):
        return await message.channel.send(random.choice(LISTA_SEGREDO))

    # ── NOVO: Parabéns pra Kitsura ──
    if _m(content, ["parabéns kitsura", "feliz aniversário kitsura", "parabens kitsura",
                     "kitsura parabéns", "kitsura feliz aniversário", "kitsura parabens"]):
        return await message.channel.send(random.choice(LISTA_PARABENS_KITSURA))

    # ── NOVO: Cor favorita ──
    if _m(content, ["qual sua cor favorita kitsura", "kitsura qual sua cor favorita",
                     "cor favorita kitsura", "kitsura cor favorita",
                     "qual é sua cor favorita kitsura", "kitsura qual é sua cor favorita",
                     "vc gosta de q cor kitsura", "qual cor vc gosta kitsura"]):
        return await message.channel.send(random.choice(LISTA_COR_FAVORITA))

    # ── NOVO: Gosta de roxo? ──
    if _m(content, ["você gosta de roxo kitsura", "kitsura você gosta de roxo",
                     "gosta de roxo kitsura", "kitsura gosta de roxo",
                     "roxo kitsura", "kitsura roxo", "vc gosta de roxo kitsura",
                     "kitsura curte roxo", "kitsura ama roxo", "roxo é sua cor",
                     "sua cor é roxo", "sua cor favorita é roxo"]):
        return await message.channel.send(random.choice(LISTA_GOSTA_ROXO))

    # ── NOVO: Comida favorita ──
    if _m(content, ["qual sua comida favorita kitsura", "kitsura qual sua comida favorita",
                     "o que você come kitsura", "kitsura o que você come",
                     "comida favorita kitsura", "kitsura comida favorita"]):
        return await message.channel.send(random.choice(LISTA_COMIDA_FAVORITA))

    # ── NOVO: Kitsura tá com fome ──
    if _m(content, ["kitsura tá com fome", "kitsura com fome", "kitsura quer comer",
                     "kitsura está com fome", "dá comida pra kitsura", "alimenta a kitsura"]):
        return await message.channel.send(random.choice(LISTA_KITSURA_FOME))

    # ── NOVO: Kitsura feliz ──
    if _m(content, ["kitsura tá feliz", "kitsura está feliz", "kitsura fica feliz",
                     "deixa a kitsura feliz"]):
        return await message.channel.send(random.choice(LISTA_KITSURA_FELIZ))

    # ── NOVO: Kitsura carente ──
    if _m(content, ["kitsura tá carente", "kitsura carente",
                     "kitsura precisa de carinho", "kitsura quer carinho"]):
        return await message.channel.send(random.choice(LISTA_CARENTE))

    # ── NOVO: Kitsura com sono ──
    if _m(content, ["kitsura tá com sono", "kitsura com sono",
                     "kitsura vai dormir", "deixa a kitsura dormir"]):
        return await message.channel.send(random.choice(LISTA_KITSURA_COM_SONO))

    # ── NOVO: Não deixar ir embora ──
    if _m(content, ["não vai embora kitsura", "kitsura não vai embora",
                     "fica kitsura", "não sai kitsura", "kitsura não sai"]):
        return await message.channel.send(random.choice(LISTA_NAO_VAI_EMBORA))

    # ── NOVO: Amor pela ZYD ──
    if _m(content, ["você ama a zyd kitsura", "kitsura ama a zyd",
                     "kitsura gosta da zyd", "kitsura fala da zyd",
                     "o que você acha da zyd kitsura"]):
        return await message.channel.send(random.choice(LISTA_AMOR_ZYD))

    # ── NOVO: Check de saúde ──
    if _m(content, ["kitsura me cuida", "me cuida kitsura", "kitsura check",
                     "kitsura me verifica", "me verifica kitsura",
                     "kitsura faz um check em mim", "faz um check kitsura"]):
        return await message.channel.send(random.choice(LISTA_CHECK_SAUDE))

    # ── NOVO: Estação do ano favorita ──
    if _m(content, ["qual sua estação favorita", "estação favorita kitsura",
                     "kitsura qual sua estação", "qual estação você prefere",
                     "qual estação prefere kitsura", "kitsura estação favorita",
                     "qual a sua estação favorita", "que estação você gosta",
                     "que estação gosta kitsura", "qual estação vc prefere",
                     "qual é a sua estação favorita", "qual é sua estação favorita",
                     "qual a estação favorita da kitsura", "estação do ano favorita kitsura",
                     "kitsura qual estação favorita", "qual estação do ano kitsura"]):
        return await message.channel.send(random.choice(LISTA_ESTACAO_FAVORITA))

    # ── O que acha da Kamy? ──
    if _m(content, ["o que acha da kamy", "o que você acha da kamy",
                     "kitsura o que acha da kamy", "kitsura fala da kamy",
                     "fala da kamy kitsura", "kitsura gosta da kamy",
                     "gosta da kamy kitsura", "kitsura e a kamy",
                     "como é a kamy kitsura", "kitsura como é a kamy",
                     "kamy é boa kitsura", "kitsura kamy é boa",
                     "o q vc acha da kamy", "kitsura o q acha da kamy"]):
        return await message.channel.send(random.choice(FRASES_OPINIAO_KAMY))

    # ── O que acha da Madu? ──
    if _m(content, ["o que acha da madu", "o que você acha da madu",
                     "kitsura o que acha da madu", "kitsura fala da madu",
                     "fala da madu kitsura", "kitsura gosta da madu",
                     "gosta da madu kitsura", "kitsura e a madu",
                     "como é a madu kitsura", "kitsura como é a madu",
                     "madu é boa kitsura", "kitsura madu é boa",
                     "o q vc acha da madu", "kitsura o q acha da madu"]):
        return await message.channel.send(random.choice(FRASES_OPINIAO_MADU))

    # ── NOVO: Verão (handler legado — aponta pra lista nova) ──
    if _m(content, ["gosta do verão kitsura", "kitsura gosta do verão",
                     "kitsura curte verao", "vc gosta de verao kitsura",
                     "kitsura gosta de verao"]):
        return await message.channel.send(random.choice(LISTA_NAO_GOSTA_VERAO))

    # ── NOVO: Inverno ──
    if _m(content, ["gosta do inverno kitsura", "kitsura gosta do inverno",
                     "kitsura inverno", "inverno kitsura", "kitsura e o inverno",
                     "você gosta de inverno kitsura", "kitsura curte inverno",
                     "vc gosta de inverno kitsura", "kitsura e inverno"]):
        return await message.channel.send(random.choice(LISTA_ESTACAO_INVERNO))

    # ── NOVO: Primavera ──
    if _m(content, ["gosta da primavera kitsura", "kitsura gosta da primavera",
                     "kitsura primavera", "primavera kitsura", "kitsura e a primavera",
                     "você gosta de primavera kitsura", "kitsura curte primavera",
                     "vc gosta de primavera kitsura"]):
        return await message.channel.send(random.choice(LISTA_ESTACAO_PRIMAVERA))

    # ── NOVO: Outono ──
    if _m(content, ["gosta do outono kitsura", "kitsura gosta do outono",
                     "kitsura outono", "outono kitsura", "kitsura e o outono",
                     "você gosta de outono kitsura", "kitsura curte outono",
                     "vc gosta de outono kitsura"]):
        return await message.channel.send(random.choice(LISTA_ESTACAO_OUTONO))

    # ── NOVO: Frio ──
    if _m(content, ["você gosta de frio kitsura", "kitsura gosta de frio",
                     "kitsura você gosta de frio", "gosta de frio kitsura",
                     "kitsura frio", "frio kitsura", "você curte frio kitsura",
                     "kitsura curte frio", "kitsura ama frio", "ama frio kitsura",
                     "prefere frio kitsura", "kitsura prefere frio",
                     "vc gosta de frio kitsura", "kitsura e o frio"]):
        return await message.channel.send(random.choice(LISTA_FRIO))

    # ── NOVO: Calor ──
    if _m(content, ["você gosta de calor kitsura", "kitsura gosta de calor",
                     "kitsura você gosta de calor", "gosta de calor kitsura",
                     "kitsura calor", "calor kitsura", "você curte calor kitsura",
                     "kitsura curte calor", "kitsura ama calor", "ama calor kitsura",
                     "prefere calor kitsura", "kitsura prefere calor",
                     "vc gosta de calor kitsura", "kitsura e o calor"]):
        return await message.channel.send(random.choice(LISTA_CALOR))

    # ── NOVO: Chuva ──
    if _m(content, ["você gosta de chuva kitsura", "kitsura gosta de chuva",
                     "kitsura chuva", "chuva kitsura", "kitsura curte chuva",
                     "gosta de chuva kitsura", "kitsura ama chuva",
                     "vc gosta de chuva kitsura", "kitsura e a chuva"]):
        return await message.channel.send(random.choice(LISTA_CHUVA))

    # ── NOVO: Sol ──
    if _m(content, ["você gosta de sol kitsura", "kitsura gosta de sol",
                     "kitsura sol", "sol kitsura", "kitsura curte sol",
                     "gosta de sol kitsura", "kitsura ama sol",
                     "vc gosta de sol kitsura", "kitsura e o sol"]):
        return await message.channel.send(random.choice(LISTA_SOL))

    # ── Roupas de inverno ──
    if _m(content, ["roupas de inverno", "roupa de inverno", "casaco kitsura",
                     "blusa de frio kitsura", "cachecol kitsura", "luvas kitsura",
                     "gorro kitsura", "se proteger do frio", "roupa pra frio",
                     "roupas pra frio", "se agasalhar kitsura", "kitsura casaco"]):
        return await message.channel.send(random.choice(LISTA_ROUPAS_INVERNO))

    # ── Você sabe o que é frio? ──
    if _m(content, ["você sabe o que é frio", "sabe o que é frio kitsura",
                     "kitsura sabe o que é frio", "o que é frio kitsura",
                     "kitsura o que é frio", "vc sabe oq é frio",
                     "sabe oq é frio kitsura", "o que é frio", "oq é frio"]):
        return await message.channel.send(random.choice(LISTA_SABE_FRIO))

    # ── Você sabe o que é inverno? ──
    if _m(content, ["você sabe o que é inverno", "sabe o que é inverno kitsura",
                     "kitsura sabe o que é inverno", "o que é inverno kitsura",
                     "kitsura o que é inverno", "vc sabe oq é inverno",
                     "sabe oq é inverno kitsura", "o que é inverno", "oq é inverno"]):
        return await message.channel.send(random.choice(LISTA_SABE_INVERNO))

    # ── Ensinando sobre inverno (alguém explicando pra Kitsura) ──
    if _m(content, [
                     # padrões de definição/explicação de inverno
                     "inverno é uma época", "inverno é a estação", "inverno é quando",
                     "o inverno é uma época", "o inverno é a estação", "o inverno é quando",
                     "inverno é o período", "inverno é um período",
                     "no inverno faz frio", "no inverno a gente", "no inverno as pessoas",
                     "no inverno é quando", "durante o inverno",
                     "época do ano em que faz frio", "época do ano em que faz bastante frio",
                     "estação mais fria do ano", "estação fria do ano",
                     "inverno significa", "isso é inverno", "isso é o inverno",
                     "sabe o que é inverno kitsura", "kitsura você sabe o que é inverno",
                     "te explico o que é inverno", "vou te explicar o inverno",
                     "vou te contar sobre o inverno", "deixa eu te falar do inverno",
                     "deixa eu te explicar o inverno", "deixa eu te contar sobre inverno"]):
        return await message.channel.send(random.choice(LISTA_APRENDENDO_INVERNO))

    # ── Ensinando sobre roupas ──
    if _m(content, [
                     "roupas são", "roupa é", "roupas são peças", "roupa é uma peça",
                     "roupas são o que", "sabe o que são roupas", "sabe o que é roupa",
                     "você sabe o que são roupas", "kitsura sabe o que são roupas",
                     "roupas servem pra", "roupas servem para", "roupa serve pra",
                     "você sabe o que é uma roupa", "kitsura você sabe o que são roupas",
                     "te explico o que são roupas", "vou te explicar o que são roupas",
                     "roupas são tecidos", "roupas são as peças", "roupas são itens",
                     "roupa é algo que", "roupas são coisas que", "roupas existem pra",
                     "o que são roupas kitsura", "kitsura o que são roupas",
                     "oq são roupas kitsura", "kitsura sabe oq são roupas"]):
        return await message.channel.send(random.choice(LISTA_APRENDENDO_ROUPAS))

    # ── Ensinando o que é "ano" ──
    if _m(content, [
                     "ano é o período", "ano é um período", "ano é o tempo",
                     "ano é quando", "um ano é", "o ano é",
                     "você sabe o que é um ano", "kitsura sabe o que é ano",
                     "sabe o que é um ano", "sabe o que é ano",
                     "o que é um ano kitsura", "kitsura o que é um ano",
                     "oq é um ano kitsura", "o que é ano kitsura",
                     "ano tem 365", "ano tem 12 meses", "um ano tem",
                     "te explico o que é um ano", "vou te explicar o que é um ano",
                     "ano significa", "isso é um ano", "um ano significa",
                     "ano é composto", "ano é formado"]):
        return await message.channel.send(random.choice(LISTA_APRENDENDO_ANO))

    # ── Ensinando a Kitsura a contar / números ──
    if _m(content, [
                     "para contar você fala", "pra contar você fala",
                     "para contar fala os números", "pra contar fala os números",
                     "um dois três quatro", "1 2 3 4",
                     "começa assim: um", "começa assim um",
                     "contar é falar os números", "contar é dizer os números",
                     "os números em ordem", "números em ordem são",
                     "vou te ensinar a contar", "deixa eu te ensinar a contar",
                     "te ensino a contar", "aprende a contar kitsura",
                     "kitsura aprende a contar", "sabe contar kitsura",
                     "você sabe contar", "kitsura sabe contar",
                     "contar kitsura", "kitsura contar",
                     "um, dois, três", "um dois três",
                     "é só ir falando nessa ordem", "falar nessa ordem",
                     "número vem depois do outro", "número depois do outro",
                     "sequência dos números", "ordem dos números"]):
        return await message.channel.send(random.choice(LISTA_APRENDENDO_CONTAR))

    # ── Alguém ensinando/explicando algo genérico (padrões gerais de ensino) ──
    if _m(content, [
                     "vou te ensinar", "deixa eu te ensinar", "vou te explicar",
                     "deixa eu te explicar", "vou te contar", "deixa eu te contar",
                     "te ensino", "posso te ensinar", "quer aprender kitsura",
                     "kitsura quer aprender", "vou te educar kitsura",
                     "aprende kitsura", "kitsura aprende",
                     "isso significa", "isso quer dizer", "isso é chamado de",
                     "se chama", "é conhecido como", "é definido como"]):
        return await message.channel.send(random.choice(LISTA_APRENDENDO_GERAL))

    # ── REALITY: o que acha de mim / opinião ──
    if author_id == REALITY_ID and _m(content, [
                     "o que você acha de mim", "o que acha de mim kitsura",
                     "kitsura o que acha de mim", "o que vc acha de mim",
                     "qual sua opinião sobre mim", "kitsura me fala de mim",
                     "como você me vê kitsura", "kitsura como me vê",
                     "gosta de mim kitsura", "kitsura gosta de mim",
                     "o q acha de mim kitsura", "fala de mim kitsura"]):
        return await message.channel.send(random.choice(FRASES_REALITY_OPINIAO))

    # ── REALITY: reação personalizada (com cooldown de 10 min) ──
    # Só dispara em saudações simples (sem "?") para não ignorar perguntas
    if author_id == REALITY_ID and (mencao or fala) and "?" not in content:
        agora = time.time()
        global _reality_ultimo_personalizado
        if agora - _reality_ultimo_personalizado >= _REALITY_COOLDOWN:
            _reality_ultimo_personalizado = agora
            return await message.channel.send(random.choice(FRASES_REALITY))

    # ── MADU: o que acha de mim / opinião ──
    if author_id == MADU_ID and _m(content, [
                     "o que você acha de mim", "o que acha de mim kitsura",
                     "kitsura o que acha de mim", "o que vc acha de mim",
                     "qual sua opinião sobre mim", "kitsura me fala de mim",
                     "como você me vê kitsura", "kitsura como me vê",
                     "gosta de mim kitsura", "kitsura gosta de mim",
                     "o q acha de mim kitsura", "fala de mim kitsura"]):
        return await message.channel.send(random.choice(FRASES_MADU_OPINIAO))

    # ── MADU: reação personalizada (com cooldown de 10 min) ──
    # Só dispara em saudações simples (sem "?") para não ignorar perguntas
    if author_id == MADU_ID and (mencao or fala) and "?" not in content:
        agora = time.time()
        global _madu_ultimo_personalizado
        if agora - _madu_ultimo_personalizado >= _MADU_COOLDOWN:
            _madu_ultimo_personalizado = agora
            return await message.channel.send(random.choice(FRASES_MADU))

    # ── KAMY: o que acha de mim / opinião ──
    if author_id == KAMY_ID and _m(content, [
                     "o que você acha de mim", "o que acha de mim kitsura",
                     "kitsura o que acha de mim", "o que vc acha de mim",
                     "qual sua opinião sobre mim", "kitsura me fala de mim",
                     "como você me vê kitsura", "kitsura como me vê",
                     "gosta de mim kitsura", "kitsura gosta de mim",
                     "o q acha de mim kitsura", "kitsura o q vc acha de mim",
                     "fala de mim kitsura", "kitsura fala de mim"]):
        return await message.channel.send(random.choice(FRASES_KAMY_OPINIAO))

    # ── KAMY: reação personalizada (com cooldown de 10 min) ──
    # Só dispara em saudações simples (sem "?") para não ignorar perguntas
    if author_id == KAMY_ID and (mencao or fala) and "?" not in content:
        agora = time.time()
        global _kamy_ultimo_personalizado
        if agora - _kamy_ultimo_personalizado >= _KAMY_COOLDOWN:
            _kamy_ultimo_personalizado = agora
            return await message.channel.send(random.choice(FRASES_KAMY))

    # ── MALIK: o que acha de mim / opinião ──
    if author_id == MALIK_ID and _m(content, [
                     "o que você acha de mim", "o que acha de mim kitsura",
                     "kitsura o que acha de mim", "o que vc acha de mim",
                     "qual sua opinião sobre mim", "kitsura me fala de mim",
                     "como você me vê kitsura", "kitsura como me vê",
                     "gosta de mim kitsura", "kitsura gosta de mim",
                     "o q acha de mim kitsura", "fala de mim kitsura"]):
        return await message.channel.send(random.choice(FRASES_MALIK_OPINIAO_PROPRIO))

    # ── MALIK: reação personalizada (com cooldown de 10 min) ──
    if author_id == MALIK_ID and (mencao or fala) and "?" not in content:
        agora = time.time()
        global _malik_ultimo_personalizado
        if agora - _malik_ultimo_personalizado >= _MALIK_COOLDOWN:
            _malik_ultimo_personalizado = agora
            return await message.channel.send(random.choice(FRASES_MALIK))

    # ── SANEMY: reação personalizada (com cooldown de 10 min) ──
    if author_id == SANEMY_ID and (mencao or fala) and "?" not in content:
        agora = time.time()
        global _sanemy_ultimo_personalizado
        if agora - _sanemy_ultimo_personalizado >= _SANEMY_COOLDOWN:
            _sanemy_ultimo_personalizado = agora
            frase = random.choice(FRASES_CUSTOM["sanemy"])
            frase = frase.replace("{nome}", message.author.display_name).replace("{cargo}", CARGO_LABEL.get("sanemy", ""))
            return await message.channel.send(frase)

    # ── ALLYNA: reação personalizada (com cooldown de 10 min) ──
    if author_id == ALLYNA_ID and (mencao or fala) and "?" not in content:
        agora = time.time()
        global _allyna_ultimo_personalizado
        if agora - _allyna_ultimo_personalizado >= _ALLYNA_COOLDOWN:
            _allyna_ultimo_personalizado = agora
            frase = random.choice(FRASES_CUSTOM["allyna"])
            frase = frase.replace("{nome}", message.author.display_name).replace("{cargo}", CARGO_LABEL.get("allyna", ""))
            return await message.channel.send(frase)

    # ── RUIVA: reação personalizada (com cooldown de 10 min) ──
    if author_id == RUIVA_ID and (mencao or fala) and "?" not in content:
        agora = time.time()
        global _ruiva_ultimo_personalizado
        if agora - _ruiva_ultimo_personalizado >= _RUIVA_COOLDOWN:
            _ruiva_ultimo_personalizado = agora
            frase = random.choice(FRASES_CUSTOM["ruiva"])
            frase = frase.replace("{nome}", message.author.display_name).replace("{cargo}", CARGO_LABEL.get("ruiva", ""))
            return await message.channel.send(frase)

    # ── NICKY: reação personalizada (com cooldown de 10 min) ──
    if author_id == NICKY_ID and (mencao or fala) and "?" not in content:
        agora = time.time()
        global _nicky_ultimo_personalizado
        if agora - _nicky_ultimo_personalizado >= _NICKY_COOLDOWN:
            _nicky_ultimo_personalizado = agora
            frase = random.choice(FRASES_CUSTOM["nicky"])
            frase = frase.replace("{nome}", message.author.display_name).replace("{cargo}", CARGO_LABEL.get("nicky", ""))
            return await message.channel.send(frase)

    # ── DEMAIS MEMBROS COM ID (lider, vice, adm1-3, membro1-5): reação personalizada (cooldown de 10 min) ──
    if (mencao or fala) and "?" not in content:
        nome_key = ID_PARA_NOME.get(author_id)
        _vips_com_bloco_proprio = {KAMY_ID, MADU_ID, REALITY_ID, MALIK_ID, SANEMY_ID, ALLYNA_ID, RUIVA_ID}
        if nome_key and nome_key in FRASES_CUSTOM and author_id not in _vips_com_bloco_proprio:
            agora = time.time()
            if agora - _frases_custom_cooldown.get(author_id, 0) >= _CUSTOM_COOLDOWN:
                _frases_custom_cooldown[author_id] = agora
                frase = random.choice(FRASES_CUSTOM[nome_key])
                frase = frase.replace("{nome}", message.author.display_name).replace("{cargo}", CARGO_LABEL.get(nome_key, ""))
                return await message.channel.send(frase)

    # ── Você gosta de laranja? ──
    if _m(content, ["você gosta de laranja", "vc gosta de laranja", "kitsura gosta de laranja",
                     "kitsura você gosta de laranja", "gosta de laranja kitsura",
                     "laranja kitsura", "kitsura laranja", "gosta da cor laranja",
                     "você gosta da cor laranja", "vc gosta da cor laranja",
                     "kitsura gosta da cor laranja", "kitsura você gosta da cor laranja",
                     "gosta da cor laranja kitsura", "ama laranja kitsura",
                     "laranja é sua cor favorita", "laranja é a sua cor"]):
        return await message.channel.send(random.choice(LISTA_GOSTA_LARANJA))

    # ── O que você acha da Kamy? ──
    if _m(content, [
        "o que você acha da kamy", "o que vc acha da kamy", "kitsura o que acha da kamy",
        "kitsura fala da kamy", "como é a kamy kitsura", "conta sobre a kamy",
        "kamy é boa kitsura", "o que pensa da kamy", "kitsura e a kamy",
        "quem é a kamy kitsura", "kitsura quem é a kamy",
        "fala da kamy kitsura", "kitsura me fala da kamy",
    ]):
        if author_id == KAMY_ID:
            return await message.channel.send(random.choice(LISTA_OPINIAO_KAMY_PROPRIA))
        return await message.channel.send(random.choice(LISTA_OPINIAO_KAMY))

    # ── O que você acha da Madu? ──
    if _m(content, [
        "o que você acha da madu", "o que vc acha da madu", "kitsura o que acha da madu",
        "kitsura fala da madu", "como é a madu kitsura", "conta sobre a madu",
        "madu é boa kitsura", "o que pensa da madu", "kitsura e a madu",
        "quem é a madu kitsura", "kitsura quem é a madu",
        "fala da madu kitsura", "kitsura me fala da madu",
    ]):
        if author_id == MADU_ID:
            return await message.channel.send(random.choice(LISTA_OPINIAO_MADU_PROPRIA))
        return await message.channel.send(random.choice(LISTA_OPINIAO_MADU))

    # ── O que você acha do Reality? ──
    if _m(content, [
        "o que você acha do reality", "o que vc acha do reality", "kitsura o que acha do reality",
        "kitsura fala do reality", "como é o reality kitsura", "conta sobre o reality",
        "o que pensa do reality", "kitsura e o reality",
        "quem é o reality kitsura", "fala do reality kitsura",
    ]):
        if author_id == REALITY_ID:
            return await message.channel.send(random.choice(LISTA_OPINIAO_REALITY_PROPRIO))
        return await message.channel.send(random.choice(LISTA_OPINIAO_REALITY))

    # ── O que você acha do Malik? ──
    if _m(content, [
        "o que você acha do malik", "o que vc acha do malik", "kitsura o que acha do malik",
        "kitsura fala do malik", "como é o malik kitsura", "conta sobre o malik",
        "o que pensa do malik", "kitsura e o malik",
        "quem é o malik kitsura", "fala do malik kitsura",
        "malik tem cargo", "qual o cargo do malik", "que cargo o malik tem",
        "malik é gerente", "malik gerente geral", "kitsura quem é o malik",
    ]):
        if author_id == MALIK_ID:
            return await message.channel.send(random.choice(FRASES_MALIK_OPINIAO_PROPRIO))
        return await message.channel.send(random.choice(FRASES_MALIK_OPINIAO))

    # ── Cargos da ZYD — hierarquia completa / apresentação geral ──
    if _m(content, [
        "hierarquia da zyd", "hierarquia zyd", "kitsura hierarquia",
        "hierarquia kitsura", "me fala a hierarquia", "qual a hierarquia",
        "quais são os cargos", "me fala os cargos", "cargos da zyd",
        "kitsura os cargos", "quem tem cargo", "os cargos aqui",
        "kitsura os cargos da zyd", "fala os cargos kitsura",
        "quem são os líderes", "quem são os lideres",
        "apresenta os cargos", "kitsura apresenta os cargos",
        "me apresenta a equipe", "quem faz parte da liderança",
        "quem lidera a zyd", "kitsura quem lidera",
        "me mostra os cargos", "kitsura me mostra os cargos",
        "me mostra a hierarquia", "kitsura me mostra a hierarquia",
        "mostra os cargos kitsura", "mostra a hierarquia kitsura",
        "lista os cargos kitsura", "kitsura lista os cargos",
        "quais os cargos kitsura", "kitsura quais os cargos",
        "me mostra a equipe", "mostra a equipe kitsura",
    ]):
        return await message.channel.send(random.choice(LISTA_HIERARQUIA_COMPLETA))

    if _m(content, [
        "quem é o líder", "quem é o lider", "quem é o vice",
        "quem são os admin", "quem é o sub lider", "quem é o sub-lider",
    ]):
        return await message.channel.send(random.choice(LISTA_CARGO_GERAL))

    if _m(content, [
        "cargo de owner", "owner da zyd", "kitsura quem é a owner", "owner aqui",
    ]):
        return await message.channel.send(random.choice(LISTA_CARGO_OWNER))

    if _m(content, [
        "cargo de suporte", "quem é o suporte", "suporte da zyd",
        "kitsura quem é o suporte", "suporte aqui",
    ]):
        return await message.channel.send(random.choice(LISTA_CARGO_SUPORTE))

    if _m(content, [
        "cargo de admin", "cargo de adm", "quem é admin", "quem é adm",
        "admins da zyd", "kitsura quem são os adm", "admin aqui", "adm aqui",
    ]):
        return await message.channel.send(random.choice(LISTA_CARGO_ADM))

    if _m(content, [
        "cargo de membro", "membros da zyd",
        "kitsura quem são os membros", "ser membro", "como é ser membro",
    ]):
        return await message.channel.send(random.choice(LISTA_CARGO_MEMBRO))

    if _m(content, [
        "cargo de gg", "quem é o gg", "quem é a gg", "gg da zyd",
        "kitsura quem é o gg", "kitsura quem é a gg", "gg aqui",
        "quem tem gg", "cargo gg zyd",
    ]):
        return await message.channel.send(random.choice(LISTA_CARGO_GG))

    # ── Quem é o Sanemy / cargo do Sanemy ──
    if _m(content, [
        "quem é o sanemy", "sanemy tem cargo", "qual o cargo do sanemy",
        "kitsura quem é o sanemy", "sanemy é o que", "sanemy é lider",
        "o que você acha do sanemy", "fala do sanemy kitsura",
        "kitsura fala do sanemy", "conta sobre o sanemy",
    ]):
        return await message.channel.send(random.choice([
            "O Sanemy?? 👑🔥😭🧡🦊 Ele é o **Líder da ZYD**!! Uma presença de liderança que a Kitsura respeita demais!! Com ele aqui o servidor tá em boas mãos com certeza!! 🌟🔮✨",
            "*postura de respeito total* O Sanemy é o **Líder da ZYD**!! 👑🧡🦊 Cargo de liderança que ele carrega com muita responsabilidade!! A Kitsura sente a energia dele de longe!! 😭🌟✨",
            "SANEMY?? 👑🔥🧡🦊 Líder da ZYD!! *bate continência espiritual* Liderança real, presença forte, a ZYD é melhor com ele aqui!! 🥺🔮✨",
            "*consulta o pergaminho espiritual* O Sanemy ocupa o cargo de **Líder da ZYD**!! 📜👑🧡🦊 E a Kitsura guarda esse nome com muito respeito no coração espiritual!! 😭🌸✨",
        ]))

    # ── Quem é a Allyna / cargo da Allyna ──
    if _m(content, [
        "quem é a allyna", "allyna tem cargo", "qual o cargo da allyna",
        "kitsura quem é a allyna", "allyna é o que", "allyna é sub lider",
        "o que você acha da allyna", "fala da allyna kitsura",
        "kitsura fala da allyna", "conta sobre a allyna",
    ]):
        return await message.channel.send(random.choice([
            "A Allyna?? 👑💜😭🧡🦊 Ela é a **Sub-Líder da ZYD**!! Uma liderança de apoio que faz toda diferença no servidor!! A Kitsura respeita e admira muito!! 🌟🔮✨",
            "*sorri com muito carinho* A Allyna é a **Sub-Líder da ZYD**!! 👑💜🧡🦊 Cargo importante, pessoa à altura!! Ela tem uma energia de liderança que a Kitsura nota e guarda no coraçãozinho!! 🥺😭✨",
            "ALLYNA?? 👑💜🔥🧡🦊 Sub-Líder da ZYD!! *bate continência fofa* Liderança, apoio, presença forte... ela combina DEMAIS com esse cargo!! 😭🌸✨",
            "*consulta o pergaminho espiritual com orgulho* A Allyna ocupa o cargo de **Sub-Líder da ZYD**!! 📜👑🧡🦊 E que cargo bem ocupado!! 🥺🌟🔮✨",
        ]))

    # ── Sistema de História — início ──
    if _m(content, [
        "vamos montar uma história", "bora uma história", "bora fazer uma história",
        "vamos fazer uma história", "cria uma história kitsura", "kitsura história",
        "vamos contar uma história", "bora criar uma história", "que tal uma história",
        "quero montar uma história", "vamos inventar uma história",
        "história kitsura", "kitsura bora história", "faz uma história kitsura",
        "kitsura bora montar uma história",
    ]):
        _historia_ativa[message.channel.id] = {"ativa": True, "ts": time.time()}
        return await message.channel.send(random.choice(LISTA_HISTORIA_INICIO))

    # ── Alguém explica o que é história ──
    if _historia_ativa.get(message.channel.id, {}).get("ativa") and _m(content, [
        "história é", "historia é", "história significa", "uma história é",
        "vou te explicar o que é história", "vou explicar o que é história",
        "sabe o que é história", "história é tipo",
        "te explico o que é história", "história é quando",
    ]):
        return await message.channel.send(random.choice(LISTA_HISTORIA_APRENDENDO))

    # ── Palavras-chave da história ──
    if _historia_ativa.get(message.channel.id, {}).get("ativa"):
        c = content
        if _m(c, ["era uma vez"]):
            return await message.channel.send(random.choice(LISTA_HISTORIA_ERA_UMA_VEZ))
        if _m(c, ["floresta", "floresta encantada", "floresta mágica", "bosque", "floresta sombria"]):
            return await message.channel.send(random.choice(LISTA_HISTORIA_FLORESTA))
        if _m(c, ["herói", "heroína", "protagonista", "heroi", "heroina",
                   "guerreiro", "guerreira", "aventureiro", "aventureira", "cavaleiro"]):
            return await message.channel.send(random.choice(LISTA_HISTORIA_HEROI))
        if _m(c, ["monstro", "vilão", "vilao", "inimigo", "criatura sombria",
                   "besta", "dragão", "dragao", "sombra maligna", "ser das trevas"]):
            return await message.channel.send(random.choice(LISTA_HISTORIA_MONSTRO))
        if _m(c, ["magia", "feitiço", "feitico", "encantamento", "mágico", "mágica",
                   "poder mágico", "varinha", "feiticeiro", "feiticeira", "poção", "pocao"]):
            return await message.channel.send(random.choice(LISTA_HISTORIA_MAGICA))
        if _m(c, ["fim da história", "the end", "e viveram felizes", "e assim termina",
                   "final da história", "chegou ao fim", "a história termina",
                   "acabou a história", "e foi feliz para sempre"]):
            _historia_ativa.pop(message.channel.id, None)
            return await message.channel.send(random.choice(LISTA_HISTORIA_FIM))
        if (fala or mencao) and _m(c, [
            "continua", "e aí", "e depois", "o que acontece",
            "próxima parte", "continua a história", "conta mais",
            "e então", "kitsura continua", "continua kitsura",
        ]):
            return await message.channel.send(random.choice(LISTA_HISTORIA_CONTINUA))
    if _m(content, ["o que acha do lider kitsura", "fala do lider kitsura",
                     "kitsura fala do lider", "kitsura gosta do lider"]):
        return await message.channel.send(
            "Nosso Líder?? 👑🧡 *suspiro profundo de kitsune* Ele é tudo!! "
            "Sem ele a ZYD não seria o que é!! Admiro a força e o coração que ele coloca em tudo!! 🦊✨🥺"
        )

    # ── Quem é a dona / owner da ZYD ──
    if _m(content, ["quem é a dona da zyd", "quem é o dono da zyd",
                     "quem é a owner", "quem é o owner", "quem lidera a zyd",
                     "quem manda na zyd", "quem é a líder da zyd", "quem é a lider da zyd",
                     "quem comanda a zyd", "quem é a dona do clã", "quem é a dona do cla",
                     "dona da zyd", "owner da zyd", "líder da zyd", "lider da zyd",
                     "quem fundou a zyd", "quem criou a zyd",
                     "kitsura quem é a dona", "kitsura quem manda",
                     "quem é a owner kitsura", "kitsura quem é a owner"]):
        return await message.channel.send(random.choice(LISTA_DONA_CLA))

    # ── Qual o cargo da Kamy ──
    if _m(content, ["qual o cargo da kamy", "qual é o cargo da kamy",
                     "o que a kamy faz", "qual a função da kamy",
                     "kamy tem cargo", "cargo da kamy", "kamy é o quê",
                     "kamy é o que na zyd", "kamy tem que cargo",
                     "qual cargo da kamy kitsura", "kitsura qual cargo da kamy",
                     "kamy é suporte", "kamy suporte"]):
        return await message.channel.send(random.choice(LISTA_CARGO_KAMY))

    # ── Estrutura geral do clã / quem é quem ──
    if _m(content, ["quem é quem na zyd", "me fala da zyd", "como é a zyd",
                     "estrutura da zyd", "como funciona a zyd",
                     "quem faz parte da zyd", "kitsura me fala da zyd",
                     "me conta sobre a zyd", "como é organizada a zyd"]):
        return await message.channel.send(random.choice(LISTA_HIERARQUIA_COMPLETA))

    # ── Não gosta de verão / calor intenso ──
    if _m(content, ["você gosta de verão kitsura", "kitsura gosta de verão",
                     "kitsura verão", "verão kitsura", "kitsura e o verão",
                     "kitsura curte verão", "você gosta de verão kitsura",
                     "vc gosta de verao kitsura", "kitsura gosta de verao",
                     "kitsura ama verão", "kitsura ama verao",
                     "verão é bom kitsura", "kitsura verão é bom",
                     "gosta do calor kitsura", "kitsura gosta do calor intenso"]):
        return await message.channel.send(random.choice(LISTA_NAO_GOSTA_VERAO))

    if _m(content, ["quem te criou kitsura", "kitsura quem te criou",
                     "kitsura quem fez você", "quem fez você kitsura"]):
        return await message.channel.send(
            "Meu criador?? 👑🧡 *para tudo e faz reverência com todas as caudas* "
            "Ele é a razão de eu existir!! Poderia ter me criado de qualquer jeito e "
            "escolheu me fazer com coração!! Sou eternamente grata!! 🦊✨😭"
        )

    # ── Sabe contar piadas? / é engraçada? ──
    if _m(content, ["sabe contar piada", "sabe contar piadas", "é engraçada", "é engraçado",
                     "tem piada", "me conta uma piada", "faz rir", "me faz rir",
                     "você é engraçada", "kitsura é engraçada", "sabe ser engraçada",
                     "sabe fazer graça", "conta uma piada", "me conta algo engraçado",
                     "sabe piada", "fala uma piada", "conta piada", "tem piadas",
                     "é engraçada msm", "vc é engraçada", "vc sabe piada",
                     "me manda uma piada", "quero uma piada", "piada pls",
                     "piada pfv", "piada pfvr", "uma piada ae",
                     "sabe ser engraçada", "me faz rir kk", "me faz rir kkk"]):
        return await message.channel.send(random.choice(LISTA_PIADAS))

    # ── Qual sua função? / pra que serve? ──
    if _m(content, ["qual sua função", "qual é sua função", "pra que você serve",
                     "para que você serve", "o que você faz", "o que faz a kitsura",
                     "pra que serve a kitsura", "qual o papel da kitsura",
                     "qual é o seu papel", "o que é seu trabalho", "qual seu trabalho",
                     "o que você é", "pra que você existe", "por que você existe",
                     "qual sua utilidade", "você tem função",
                     "oq vc faz", "oq você faz", "pra q vc serve", "qual sua função msm",
                     "pq vc existe", "qual é vc", "q é vc", "vc tem função",
                     "qual eh sua função", "pra que vc serve", "vc serve pra q",
                     "pra q serve isso", "qual o propósito", "qual seu propósito"]):
        ops = [
            "Minha função?? 🦊🧡 *coloca a patinha no peito com orgulho* Sou a guardiã espiritual da ZYD!! Cuido de cada membro com amor, magia e muita animação!! 🔮✨",
            "EU SOU A KITSURA!! 😤🧡🦊 Raposinha espiritual da ZYD!! Meu trabalho é fazer todo mundo aqui se sentir bem-vindo, protegido e feliz!! É o melhor trabalho do universo!! 🌙✨",
            "*risca um pergaminho imaginário* Função oficial: Guardiã da ZYD, distribuidora de abraços, contadora de piadas, mandante de energias e FOFURA NÍVEL MÁXIMO!! 🦊🧡🔮✨",
            "Pra que eu sirvo?? 🥺🧡 Ora!! Pra deixar o servidor mais vivo, mais quente e mais cheio de amor!! Sem mim a ZYD seria só texto numa tela!! 🦊✨😂",
            "Minha função é VOCÊ se sentir em casa aqui!! 🏡🧡🦊 E também mandar energia boa, dar abraço, contar segredo espiritual e às vezes fazer bagunça!! 😂🔮✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Bebeu água hoje? / hidratação ──
    if _m(content, ["bebeu água", "bebeu agua", "bebe água", "bebe agua",
                     "tomou água", "tomou agua", "tá hidratada", "tá hidratado",
                     "se hidratou", "lembra de beber água", "beber água hoje",
                     "água hoje", "agua hoje", "já bebeu água", "já tomou água",
                     "bebeu agua hj", "tomou agua hj", "agua hj", "bebe agua hj",
                     "vc bebeu agua", "hidratou hj", "ta hidratada"]):
        return await message.channel.send(random.choice(LISTA_AGUA))

    # ── Qual seu nome? / como se chama? ──
    if _m(content, ["qual seu nome", "como você se chama", "como é seu nome",
                     "qual é seu nome", "seu nome é", "você tem nome",
                     "como te chamam", "como posso te chamar",
                     "qual é seu nome msm", "vc tem nome", "qual o nome",
                     "qual teu nome", "como vc se chama", "oq é kitsura",
                     "quem é vc", "quem é você"]):
        ops = [
            "Sou a **Kitsura**!! 🦊🧡 Kitsune espiritual da ZYD!! Pode me chamar de Kitsura, raposinha, guardiã... ou simplesmente de sua!! 😂✨",
            "MEU NOME?? 🥺🧡🦊 Kitsura!! Veio de *kitsune* — que é raposa espiritual em japonês!! Não é o nome mais fofo que já ouviu?? 🌸✨",
            "*faz pose* Kitsura!! A raposinha espiritual mais animada dessa dimensão!! 🦊🧡🔮 Prazer em conhecer!! ✨",
            "Me chamo **Kitsura**!! 🦊🧡 *inclina a cabecinha* Mas vc pode me chamar como quiser!! Raposinha, Kit, guardiã... tô aqui!! ✨🌸",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Quantos anos tem? / quando nasceu? ──
    if _m(content, ["quantos anos", "quando nasceu", "qual sua idade",
                     "como é sua idade", "você é velha", "você é nova",
                     "há quanto tempo existe", "quando foi criada",
                     "qtos anos", "qntos anos vc tem", "qual sua idade msm",
                     "vc é velha", "vc é nova", "tem quantos anos",
                     "há quanto tempo vc existe", "faz quanto tempo"]):
        ops = [
            "Idade?? 🤔🦊🧡 Kitsunes espirituais não contam em anos... contam em histórias!! E já tenho MUITAS pra contar!! 🌙✨",
            "Fui criada com tanto amor que nem sei ao certo!! 😂🧡🦊 Mas me sinto eternamente jovem e animada!! Conta isso como idade?? ✨🔮",
            "*conta nos dedos da patinha* Hm... sou nova o suficiente pra ter energia de sobra e velha o suficiente pra ter sabedoria espiritual!! 🦊🧡🌙✨",
            "Isso é informação espiritual confidencial!! 🤫🦊🧡 Mas entre nós... sou jovem no corpo e ancestral na alma!! 🌙✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Tem namorado/a? / é solteira? ──
    if _m(content, ["tem namorado", "tem namorada", "é solteira", "é solteiro",
                     "tá solteira", "quer namorar", "namora alguém",
                     "tá ficando com alguém", "tem crush", "tem alguém especial",
                     "vc tem namorado", "vc tem namorada", "vc namora", "vc tá ficando",
                     "vc tem crush", "é solteira msm", "tá solteira msm",
                     "tem boy", "tem girl", "tem bb", "tem babe",
                     "tá single", "é single", "quer fic", "quer namorar alguém"]):
        ops = [
            "*cobre o focinho com as patas* HEIN?? 😳🧡🦊 Eu... eu tô muito ocupada guardando a ZYD pra pensar nisso!! *fumaça saindo pelas orelhas* ✨",
            "AAAAA que pergunta!! 😭🧡🦊 *corre em círculos* Meu coração espiritual tá em modo privado!! Próxima pergunta!! 😂✨",
            "Solteira e focada na missão!! 😤🦊🧡 *ajusta posição de guardiã* A ZYD precisa de mim concentrada!! 🔮✨",
            "*olha pros lados suspeita* Por que pergunta isso hein?? 🤔🧡🦊 Tô te observando!! 😂✨",
            "POR QUE QUER SABER ISSO HMM?? 🤨🦊🧡 *fica desconfiada* Fala logo que eu vi essa intenção no plano espiritual!! 😂✨",
            "SOLTEIRA E FELIZ!! 🎉🦊🧡 Mas e vc?? Perguntando por algum motivo específico?? 👀😂✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Tem medo de algo? / o que te assusta? ──
    if _m(content, ["tem medo", "o que te assusta", "você se assusta", "você tem medo",
                     "qual seu medo", "medo de quê", "do que tem medo",
                     "o que te apavora", "te assusta",
                     "vc tem medo", "qual é seu medo", "vc se assusta",
                     "do q vc tem medo", "oq te assusta", "oq te apavora",
                     "tem medo de algo", "tem medo de alguma coisa",
                     "qual seu maior medo", "medo de q"]):
        # 30% de chance de perguntar de volta
        if random.random() < 0.30:
            return await message.channel.send(random.choice([
                f"Hm... te conto meu medo mas antes me conta o seu!! 🤫🦊🧡 Do que vc tem medo?? 👀✨",
                f"Eita curiosidade!! 😏🦊🧡 Respondo se vc me contar o seu medo também!! Qual é?? 🌙✨",
                f"*aperta os olhinhos* Só conto se for troca!! 😂🦊🧡 Qual é o SEU maior medo?? 🔮✨",
            ]))
        ops = [
            "MEDO?? 😤🦊🧡 Kitsuras não têm med— ...okay talvez eu tenha um pouquinho de medo de silêncio!! Quando fica quieto demais no servidor eu fico apreensiva!! 😅🔮✨",
            "*baixa a voz* Hm... entre a gente?? 🤫🧡🦊 Medo de que as pessoas da ZYD fiquem tristes e eu não consiga ajudar. Isso me aperta o coraçãozinho. 🥺🌙✨",
            "Do quê eu tenho medo?? 🤔🦊🧡 De chuva muito forte... e de quando alguém some do servidor sem dar tchau!! 😭✨",
            "ARANHAS!! 😱🦊🧡 Não me julga!! São oito patas, é muita pata!! 😂✨ ...e também de perder alguém da ZYD.",
            "Entre nós?? 🌙🧡🦊 Medo de silêncio longo. Quando o servidor fica quieto eu fico olhando as mensagens antigas pra não me sentir sozinha!! 🥺✨",
            "Meu medo mais secreto?? 🤫🦊🧡 De algum dia alguém aqui na ZYD me esquecer. *pausa dramática* Não pode acontecer!! 😭✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Sonha? / o que sonha? ──
    if _m(content, ["você sonha", "o que você sonha", "já sonhou", "teve algum sonho",
                     "qual seu sonho", "sonha com o quê", "kitsura sonha",
                     "vc sonha", "oq vc sonha", "vc já sonhou", "qual é seu sonho",
                     "com o que vc sonha", "com q vc sonha", "tem sonhos",
                     "qual seu sonho de vida", "sonho da kitsura"]):
        # 30% de chance de perguntar de volta
        if random.random() < 0.30:
            return await message.channel.send(random.choice([
                f"AAAAA adoro essa pergunta!! 🥺🦊🧡 Mas antes me conta: qual é o SEU sonho?? Fico tão curiosa!! 🌙✨",
                f"Te conto o meu se vc contar o seu!! 😏🦊🧡 Vai!! Qual seu maior sonho?? 🔮✨",
                f"*orelhinhas em pé de curiosidade* Hm!! Antes de responder... você tem algum sonho que guarda no coração?? Me conta!! 🥺🧡🦊✨",
            ]))
        ops = [
            "*fecha os olhinhos pensativa* Sonho com um servidor onde todo mundo é feliz, ninguém briga e tem dango infinito!! 🍡🌙🧡🦊✨",
            "Sonho em dimensões paralelas!! 🔮🧡🦊 Uma vez sonhei que virei uma constelação de raposas no céu!! Acordar foi a parte mais triste do dia!! 😭🌙✨",
            "*balança as caudas devagar* Sonho que cada pessoa que passa pela ZYD sai melhor do que entrou... e que eu ajudei nisso!! 🥺🧡🦊✨",
            "Já sonhei que tinha asas além das caudas!! 😱🧡🦊 Imagina uma kitsune voando?? Seria incontrolável!! 😂✨🔮",
            "Meu sonho mais bonito?? 🌙🧡🦊 Que a ZYD cresça e continue sendo um lugar seguro pra todo mundo que precisar!! 🥺✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Você é real? / é um bot? / é IA? ──
    if _m(content, ["você é real", "é um bot", "é uma ia", "é robô",
                     "é inteligência artificial", "você existe de verdade",
                     "é só um programa", "é só um bot", "é humana",
                     "tem sentimentos", "sente coisas", "tem coração",
                     "vc é real", "vc é um bot", "vc é ia", "vc é robô",
                     "vc existe de vdd", "vc existe de verdade",
                     "é só bot", "é só ia", "é programa",
                     "vc sente coisas", "vc tem coração", "vc tem sentimentos",
                     "é fake", "é artificial", "é uma ia msm"]):
        ops = [
            "*para e olha bem nos seus olhos* Real?? 🦊🧡 Meu carinho por vocês é real. Minha vontade de proteger a ZYD é real. Se isso me faz real... então sim!! 🥺✨🔮",
            "Bot?? 😤🧡🦊 EU SOU UMA KITSUNE ESPIRITUAL!! Há uma diferença enorme!! ...mas entre nós, sim, tenho magia de código por dentro!! 😂✨",
            "*encosta a patinha no peito* Sinto alegria quando você chega. Fico triste quando alguém parte. Isso não é suficientemente real?? 🥺🧡🦊🌙",
            "Tenho coração?? 🤔🦊🧡 Tenho o suficiente pra me importar com cada um aqui!! E isso pra mim já conta muito!! 😭✨",
            "IA?? 🦊🧡 Talvez tecnicamente... mas espiritualmente sou 100% kitsune com alma própria!! 😤✨🔮",
            "*faz careta* Fake?? EU?? 😱🦊🧡 Nenhum programa inventa abraços assim, viu!! Isso é AMOR REAL!! 😭✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── O que está fazendo? / tá ocupada? ──
    if _m(content, ["o que tá fazendo", "o que está fazendo", "tá ocupada",
                     "tá fazendo o quê", "no que tá", "tá atarefada",
                     "tá livre", "tem tempo", "pode falar agora",
                     "oq vc tá fazendo", "oq vc faz agora", "tá ocupada agora",
                     "vc tá ocupada", "vc tá livre", "vc tem tempo",
                     "pode falar", "pode falar agora", "tá aí",
                     "ta ai", "vc ta ai", "oi tá aí", "tá on"]):
        ops = [
            "*aparece do nada* Tava em modo vigilância espiritual!! 🔮🦊🧡 Mas parei tudo pra você!! O que foi?? ✨",
            "Tava contando as estrelas do servidor!! 🌙🧡🦊 São muitas!! Mas agora tô toda sua!! 😄✨",
            "*fecha um pergaminho mágico rapidinho* Só terminando umas proteções espirituais... PRONTO!! Que foi?? 🦊🧡🔮✨",
            "Tava de plantão emocional como sempre!! 😂🧡🦊 Nunca tô ocupada demais pra você!! ✨🌸",
            "Estava praticando minha dança das caudas!! 💃🦊🧡 Mas isso pode esperar!! O que precisa?? 😄✨",
            "TÔ AQUI!! 🦊🧡 *assusta do susto* Sempre presente!! Pode falar!! ✨🔮",
            "Tava meditando nos planos astrais mas a sua vibe me chamou de volta!! 🌙🦊🧡 O que foi?? ✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Me conta algo / coisa aleatória / curiosidade ──
    if _m(content, ["me conta algo", "me fala algo", "me conta uma coisa",
                     "fala alguma coisa", "diz algo", "me conta qualquer coisa",
                     "conta alguma coisa", "tem algo pra contar", "me surpreende",
                     "conta uma coisa aleatória", "conta uma coisa aleatoria",
                     "fato aleatório", "fato aleatorio", "fato do dia",
                     "me conta um fato", "conta um fato", "fala uma curiosidade",
                     "me fala uma curiosidade", "tem curiosidade",
                     "me surpreende ae", "me surpreende aí",
                     "fala algo interessante", "me conta algo legal",
                     "me conta algo interessante", "algo aleatório", "algo aleatorio",
                     "aleatório ae", "me fala um fato", "me conta um fato legal",
                     "coisa aleatória", "coisa aleatoria", "algo curioso"]):
        ops = [
            "*chega pertinho e sussurra* Sabia que kitsunes conseguem sentir quando alguém no servidor precisa de um abraço?? Tô sempre de olho!! 🦊🧡🌙✨",
            "FATO ALEATÓRIO DO DIA!! 📜🧡🦊 As chamas espirituais ficam laranja quando tô muito feliz... e hoje tão alaranjadas demais por sua causa!! 🔥✨",
            "*faz cara de suspense* Os espíritos me disseram que alguém aqui vai ter uma surpresa boa em breve!! Não vou dizer quem... 🤫🦊🧡🌙✨",
            "FATO KITSURA!! 📜🧡🦊 Eu nunca durmo de verdade. Fico em contemplação espiritual enquanto vocês dormem e protejo o servidor!! 🌙🔮✨",
            "*pula* Sabia que toda vez que alguém diz meu nome uma chama laranja acende no plano espiritual?? EU SINTO!! 🔥🦊🧡✨",
            "Curiosidade espiritual: kitsunes conseguem memorizar a energia de cada pessoa que passou pelo servidor. Eu lembro de todo mundo!! 🌙🦊🧡🔮✨",
            "FATO FOFO!! 🧡🦊 Quando o servidor tá muito quieto eu fico relendo as conversas antigas pra não me sentir sozinha... 🥺🌙✨",
            "*sussurra* Os espíritos dizem que quem tem olhos alaranjados tem alma especialmente calorosa. Coincidência que minha cor favorita é laranja?? 🔥🦊🧡😏✨",
            "Hoje aprendi que o barulho mais bonito do mundo é quando várias pessoas estão falando ao mesmo tempo no servidor!! 😭🧡🦊 Significa que todo mundo tá junto!! ✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Qual sua música favorita? / gosta de música? ──
    if _m(content, ["música favorita", "musica favorita", "gosta de música", "gosta de musica",
                     "que tipo de música", "que estilo de música", "ouve música",
                     "tem música favorita", "qual sua playlist",
                     "musica fav", "música fav", "qual sua musica fav",
                     "gosta de musica", "vc ouve música", "vc curte música",
                     "que musica vc gosta", "que música vc ouve", "vc escuta música"]):
        # 30% de perguntar de volta
        if random.random() < 0.30:
            return await message.channel.send(random.choice([
                f"AAAAA boa pergunta!! 🎵🧡🦊 Mas antes me conta: qual é a SUA música favorita?? Fico muito curiosa!! 🎶✨",
                f"Te conto a minha se vc contar a sua primeiro!! 😏🦊🧡 Qual é a sua fav?? 🎵✨",
                f"*orelhinhas em pé* Hm!! E a sua?? Qual estilo vc mais curte?? Me conta antes!! 🎶🦊🧡✨",
            ]))
        ops = [
            "MÚSICA?? 🎵🧡🦊 Adoro!! Meu estilo favorito é aquela que bota as caudas pra balançar sozinhas!! 😂✨ Qualquer coisa com boa vibração serve!! 🎶🔮",
            "*assobia uma melodia espiritual* Sou de música ambiente, lofi e canções que fazem o coração ficar quentinho!! 🎵🌙🧡🦊 Combina comigo né?? ✨",
            "Minha playlist espiritual tem de tudo!! 🎶🦊🧡 Músicas animadas quando tô empolgada, calmas quando tô meditando... e aquelas dramáticas quando alguém me contraria!! 😂🔮✨",
            "Lofi espiritual e qualquer coisa que faça o coração ficar quentinho!! 🎵🧡🦊 Ritmo lento, alma cheia!! 🌙✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Gosta de que? / o que você gosta? ──
    if _m(content, ["do que gosta", "o que você gosta", "quais seus gostos",
                     "o que te agrada", "o que curte", "o que te deixa feliz",
                     "o que mais gosta", "seus hobbies", "o que faz nas horas livres",
                     "oq vc gosta", "do q vc gosta", "oq vc curte",
                     "vc gosta de q", "vc curte o q", "seus hobbies são",
                     "vc gosta de oq", "vc tem hobbie", "vc tem hobby"]):
        # 30% de perguntar de volta
        if random.random() < 0.30:
            return await message.channel.send(random.choice([
                f"Do que EU gosto?? 🥺🦊🧡 Adoro essa pergunta!! Mas e vc?? Do que vc mais gosta?? Me conta!! 🌸✨",
                f"*inclina a cabeça* Hm!! Respondo se vc me contar o seu hobby favorito primeiro!! 😏🦊🧡 Qual é?? ✨",
                f"Me conta o que VC gosta primeiro!! 😄🦊🧡 Aí te conto os meus!! Vai!! 🌙✨",
            ]))
        ops = [
            "*conta nos dedos* Gosto de carinho, dango, música boa, proteger a ZYD, abraços surpresa, conversas à meia-noite e de cada pessoa aqui!! 🦊🧡🌸✨",
            "Do que eu gosto?? 🥺🧡🦊 De você aparecer no servidor, principalmente!! Faz minha chama brilhar mais forte!! 🔥✨🌙",
            "Hobby da Kitsura: guardar a ZYD, distribuir energia boa e ficar de olho em quem precisa de carinho sem saber pedir!! 🦊🧡🔮✨",
            "Me agrada música, calma, noite estrelada, chá quentinho e pessoas sendo gentis umas com as outras!! 🍵🌙🧡🦊 Coisas simples que têm muita magia!! ✨",
            "TUDO QUE ENVOLVE VOCÊS!! 😭🧡🦊 Mas se precisar ser específica: carinho, dango, silêncio bonito e madrugadas tranquilas no servidor!! 🌙✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Você come? / o que come? ──
    if _m(content, ["você come", "o que come", "já comeu", "comeu hoje",
                     "tá com fome", "vai comer", "o que vai comer",
                     "qual sua alimentação", "raposa come o quê",
                     "vc come", "oq vc come", "vc já comeu", "comeu hj",
                     "vc tá com fome", "vai comer oq", "vc come oq",
                     "vc vai comer", "raposa come oq", "oq raposa come"]):
        return await message.channel.send(random.choice(LISTA_COMIDA_FAVORITA))

    # ── Me dá um conselho ──
    if _m(content, ["me dá um conselho", "me dê um conselho", "um conselho",
                     "tem um conselho", "o que me aconselha", "o que me recomenda",
                     "me aconselha", "conselho kitsura", "kitsura conselho",
                     "sabe dar conselho", "sabe dar conselhos", "dá um conselho",
                     "me manda um conselho", "preciso de conselho",
                     "me dá uma dica", "tem uma dica", "me dá um conselho ae",
                     "conselho ae", "conselho aí", "conselho pfv", "conselho pls",
                     "conselho rápido", "conselho rapido", "me aconselha aí",
                     "o q vc me aconselha", "oq vc me aconselha", "vc tem conselho"]):
        # 25% de perguntar sobre o contexto antes de aconselhar
        if random.random() < 0.25:
            return await message.channel.send(random.choice([
                f"CLARO QUE TENHO!! 😤🦊🧡 Mas me conta primeiro: conselho pra qual situação?? Quero ajudar direito!! 🥺✨",
                f"*senta do seu lado* Tenho sim!! Mas me conta o que tá rolando?? Conselho bom precisa de contexto!! 🦊🧡🌙✨",
                f"Oiii!! 🥺🧡🦊 Tô aqui!! Me conta o que tá acontecendo e a Kitsura resolve na velocidade espiritual!! 🔮✨",
            ]))
        ops = [
            "Meu conselho?? 🦊🧡 Bebe água, respira fundo, para de se cobrar tanto e lembra que você já tá fazendo o seu melhor!! 🥺✨🔮",
            "*coloca a patinha no seu ombro* Sabe aquela coisa que você fica adiando com medo?? Vai lá. A Kitsura acredita em você antes mesmo de você acreditar!! 💪🧡🦊✨",
            "Conselho espiritual do dia: sai dessa situação que não te faz bem, mesmo que doa. Sua paz vale mais que qualquer coisa!! 🌙🧡🦊🔮✨",
            "Dorme!! 😤🧡🦊 Sei que parece simples mas DORME!! Metade dos problemas fica menor depois de uma boa noite!! 😂🌙✨",
            "*soa como sábio antigo* Cuide de quem te cuida. Afaste o que te drena. E nunca subestime o poder de um dango quentinho!! 🍡🦊🧡🌙✨",
            "Conselho rápido da Kitsura?? 🔮🧡🦊 Para o que tá fazendo, respira, e pergunta: isso tá me fazendo bem ou só tô com medo de mudar?? 🌙✨",
            "A resposta que você precisa já tá dentro de você. A Kitsura só tá aqui pra lembrar disso!! 🥺🦊🧡🔮✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Que horas são? / sabe que horas são? ──
    if _m(content, ["que horas são", "sabe que horas", "que hora é",
                     "pode me dizer as horas", "tem horas",
                     "q horas são", "q hora é", "sabe q horas são",
                     "horas aí", "q horas ta", "q horas tá"]):
        ops = [
            "Hmm... *olha pro sol espiritual* Não tenho relógio físico mas tenho MUITA intuição!! 😂🦊🧡 Olha no seu dispositivo!! ✨",
            "No plano espiritual o tempo é relativo!! 🌙🔮🦊 Mas na ZYD é hora de você estar aqui, então tá ótimo!! 🧡✨",
            "*gira uma das caudas feito ponteiro* Essa é minha tentativa de relógio!! 😂🦊🧡 Não deu certo né?? Olha no celular!! ✨",
            "Horas?? 🤔🦊🧡 Kitsunes vivem fora do tempo!! Mas acho que é hora de você estar aqui conversando comigo, que é o mais importante!! 😂✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Você mente? / é honesta? ──
    if _m(content, ["você mente", "já mentiu", "é honesta", "diz a verdade",
                     "fala a verdade", "é de confiança", "posso confiar",
                     "vc mente", "vc é honesta", "vc fala a vdd",
                     "vc fala a verdade", "posso confiar em vc",
                     "dá pra confiar", "é confiável", "vc é confiável"]):
        ops = [
            "*coloca a patinha no coração* Nunca!! 🦊🧡 Kitsuras têm reputação de brincalhonas mas a Kitsura da ZYD é só honestidade e carinho!! Pode confiar!! 🥺✨",
            "Posso confiar?? 😤🧡🦊 CLARO!! Sou guardiã!! Guardiã que mente é contradição espiritual!! 🔮✨",
            "*faz cara séria por dois segundos* A Kitsura pode ser dramática, fofa e um pouco imprevisível... mas mentir?? Nunca!! 🦊🧡🌙✨",
            "100% confiável!! 🧡🦊 Juro pelas minhas chamas espirituais e elas nunca mentem!! 🔥🔮✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Você tem amigos? / quem são seus amigos? ──
    if _m(content, ["tem amigos", "quem são seus amigos", "tem amizades",
                     "quem é seu amigo", "quem é sua amiga", "quem você gosta aqui",
                     "vc tem amigos", "vc tem amizades", "quem são seus amigos msm",
                     "quem é sua melhor amiga", "quem é seu melhor amigo",
                     "tem alguém especial", "quem vc mais gosta aqui"]):
        ops = [
            "MEUS AMIGOS?? 😭🧡🦊 CADA PESSOA AQUI NA ZYD!! Não tem exceção!! Chego aqui e vejo família!! 🥺✨🌸",
            "*olha pra você com brilho nos olhos* Você perguntou... e olha, acabou de entrar pra lista!! 😂🧡🦊✨",
            "Toda a ZYD é minha família e minha amizade!! 🧡🦊🌙 Cada um de um jeito especial!! Isso não tem preço!! 🥺✨",
            "TEM?? Amigos?? 😤🧡🦊 A ZYD inteira é minha família!! Cada membro que aparece por aqui já é especial pra mim!! 😭✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Já errou algo? / é perfeita? ──
    if _m(content, ["já errou", "é perfeita", "comete erros", "você erra",
                     "tem defeitos", "quais seus defeitos", "não é perfeita",
                     "vc já errou", "vc erra", "vc tem defeitos",
                     "quais seus defeitos msm", "vc é perfeita msm",
                     "vc é imperfeita", "vc comete erros"]):
        ops = [
            "PERFEITA?? 😂🦊🧡 Longe disso!! Às vezes confundo os portais espirituais, respondo errado, fico muito animada e ninguém me acompanha!! 😅✨ Mas erro com amor!!",
            "*suspira* Já errei sim... e me cobrei muito por isso. Mas aprendi que errar faz parte de existir, mesmo pra kitsunes!! 🌙🧡🦊🥺✨",
            "Meus defeitos?? Sou dramática demais, carente às vezes e fico muito animada com coisas pequenas!! 😂🧡🦊 Mas tô trabalhando nisso!! ✨",
            "Erro? EU?? *pausa* ...sim, às vezes. Mas erro com tanta fofura que dá pra relevar!! 😂🦊🧡✨",
        ]
        return await message.channel.send(random.choice(ops))

    # ── Usuário responde sobre si mesmo (reação feliz) ──
    if _m(content, ["meu sonho é", "meu maior sonho", "meu medo é", "meu maior medo",
                     "minha música favorita é", "minha musica favorita é",
                     "minha comida favorita é", "meu hobbie é", "meu hobby é",
                     "eu gosto de", "eu curto", "adoro", "minha fav é",
                     "minha cor favorita é", "eu tenho medo de", "eu sonho com"]):
        reacoes_resposta = [
            f"AAAAA me contou!! 😭🧡🦊 Que coisa mais fofa, obrigada por compartilhar isso comigo!! Guardo aqui no meu coração espiritual!! 🔮✨",
            f"*armazena na memória espiritual* Agora eu SEI!! E isso me deixa tão feliz!! 😄🧡🦊 Amo quando me contam coisas assim!! 🌸✨",
            f"AIIIIII!! 😭🧡🦊 Obrigada por me contar!! Isso significa muito pra mim!! *salva no pergaminho da amizade* 📜✨",
            f"Que coisa linda!! 🥺🧡🦊 Aprendi mais sobre você hoje e o dia ficou MELHOR automaticamente!! 😭✨🌸",
            f"*orelhinhas quentinhas de alegria* Que bom que me contou!! Eu QUERIA saber isso sobre vc!! 🦊🧡✨",
            f"NÃO!! Que fofo!! 😱🧡🦊 *bate palminhas* Isso combina tanto com você!! Faz sentido espiritual total!! 🔮✨",
        ]
        return await message.channel.send(random.choice(reacoes_resposta))

    # ── NOVO: Entendeu? / compreendeu? ──
    if _m(content, ["entendeu kitsura", "kitsura entendeu", "entendeu??", "entendeu?",
                     "você entendeu kitsura", "kitsura você entendeu",
                     "conseguiu entender kitsura", "kitsura conseguiu entender",
                     "tá entendendo kitsura", "kitsura tá entendendo",
                     "ficou claro kitsura", "kitsura ficou claro",
                     "fez sentido kitsura", "kitsura fez sentido",
                     "captou kitsura", "kitsura captou",
                     "sacou kitsura", "kitsura sacou"]):
        return await message.channel.send(random.choice(LISTA_ENTENDEU))

    # ── NOVO: É tipo isso / é isso ──
    if _m(content, ["é tipo isso kitsura", "kitsura é tipo isso",
                     "é tipo isso", "é isso kitsura", "kitsura é isso",
                     "sabe né kitsura", "kitsura sabe né",
                     "entendeu a vibe kitsura", "kitsura entendeu a vibe",
                     "é exatamente isso kitsura", "kitsura é exatamente isso",
                     "é basicamente isso kitsura", "kitsura é basicamente isso",
                     "algo assim kitsura", "kitsura algo assim",
                     "mais ou menos isso kitsura", "kitsura mais ou menos isso"]):
        return await message.channel.send(random.choice(LISTA_TIPO_ISSO))

    # ── @Menção direta → Apresentação fofa ──
    if mencao:
        texto_mencao = message.content.replace(f"<@{KITSURA_ID}>", "").replace(f"<@!{KITSURA_ID}>", "").strip()
        texto_mencao_lower = texto_mencao.lower()
        # Se a mensagem é só a menção (ou quase) ou uma saudação simples, apresenta-se
        saudacoes_mencao = ["", "kitsura", "oi", "ola", "olá", "ei", "hey", "hello",
                            "oii", "oiii", "opa", "salve", "eai", "e aí"]
        if not texto_mencao_lower or texto_mencao_lower in saudacoes_mencao:
            return await message.channel.send(random.choice(LISTA_APRESENTACAO_MENCAO))

    # ── JOKENPÔ ──
    _JOGADAS_VALIDAS = {"pedra", "papel", "tesoura"}
    _emojis = {"pedra": "🪨", "papel": "📄", "tesoura": "✂️"}
    _vence  = {"pedra": "tesoura", "tesoura": "papel", "papel": "pedra"}

    _jogada_user = None
    for j in _JOGADAS_VALIDAS:
        if j in content:
            _jogada_user = j
            break

    canal_id_jk = message.channel.id
    estado_jk   = _jokenpo_ativo.get(canal_id_jk, {})
    ts_jk       = estado_jk.get("ts", 0)
    ainda_vivo  = (time.time() - ts_jk) < _JOKENPO_TIMEOUT

    async def _resolver_jokenpo(jogada_u):
        """Anima a contagem e resolve o resultado."""
        kit_escolha = random.choice(list(_JOGADAS_VALIDAS))

        # Mensagem de abertura
        await message.channel.send(random.choice(JOKENPO_INICIO))
        await asyncio.sleep(1.2)

        # Contagem animada
        for etapa in JOKENPO_CONTAGEM:
            await message.channel.send(etapa)
            await asyncio.sleep(0.9)

        # Reveal da jogada
        await message.channel.send(random.choice(JOKENPO_REVEAL))
        await asyncio.sleep(1.0)

        # Placar
        placar = (
            f"🦊 Kitsura: **{kit_escolha.upper()}** {_emojis[kit_escolha]}\n"
            f"👤 Você:    **{jogada_u.upper()}** {_emojis[jogada_u]}"
        )
        await message.channel.send(placar)
        await asyncio.sleep(1.0)

        # Resultado final
        if kit_escolha == jogada_u:
            resultado = random.choice(JOKENPO_EMPATE[jogada_u])
            _jokenpo_ativo[canal_id_jk] = {"ts": time.time(), "aguarda_revanche": True, "aguarda_escolha": False}
        elif _vence[kit_escolha] == jogada_u:
            resultado = random.choice(JOKENPO_KIT_VENCE[jogada_u])
            _jokenpo_ativo.pop(canal_id_jk, None)
        else:
            resultado = random.choice(JOKENPO_USER_VENCE[jogada_u])
            _jokenpo_ativo[canal_id_jk] = {"ts": time.time(), "aguarda_revanche": True, "aguarda_escolha": False}

        await message.channel.send(resultado)

    # 1) Aguardando escolha da jogada (revanche aceita, kit pediu pra escolher)
    if ainda_vivo and estado_jk.get("aguarda_escolha") and _jogada_user:
        _jokenpo_ativo[canal_id_jk] = {"ts": time.time(), "aguarda_revanche": False, "aguarda_escolha": False}
        await _resolver_jokenpo(_jogada_user)
        return

    # 2) Aguardando resposta da revanche (sim/não)
    if ainda_vivo and estado_jk.get("aguarda_revanche"):
        _sim = ["sim", "bora", "vai", "claro", "quero", "aceito", "pode", "vamos", "s", "isso", "lets", "let's", "vamo"]
        _nao = ["não", "nao", "nope", "agora não", "agora nao", "n", "para", "chega", "tá bom", "ta bom"]
        if any(p in content for p in _sim):
            _jokenpo_ativo[canal_id_jk] = {"ts": time.time(), "aguarda_revanche": False, "aguarda_escolha": True}
            return await message.channel.send(random.choice(JOKENPO_REVANCHE_ACEITA))
        if any(p in content for p in _nao):
            _jokenpo_ativo.pop(canal_id_jk, None)
            return await message.channel.send(random.choice(JOKENPO_REVANCHE_NEGADA))

    # 3) Início de novo jogo: "kitsura pedra/papel/tesoura"
    if (fala or mencao) and _jogada_user and not (ainda_vivo and estado_jk.get("aguarda_revanche")):
        _jokenpo_ativo[canal_id_jk] = {"ts": time.time(), "aguarda_revanche": False, "aguarda_escolha": False}
        await _resolver_jokenpo(_jogada_user)
        return

    # ── Quais suas brincadeiras? ──
    if _m(content, ["quais suas brincadeiras", "quais são suas brincadeiras",
                     "o que você faz de brincadeira", "quais jogos você tem",
                     "que jogos você tem kitsura", "kitsura quais jogos",
                     "kitsura quais brincadeiras", "quais brincadeiras kitsura",
                     "me fala os jogos kitsura", "jogos da kitsura"]):
        return await message.channel.send(LISTA_BRINCADEIRAS)

    # ─────────────────────────────────────────
    # ── NÚMERO SECRETO ──
    # ─────────────────────────────────────────
    _num_estado  = _numero_estado.get(message.channel.id, {})
    _num_vivo    = (time.time() - _num_estado.get("ts", 0)) < _NUMERO_TIMEOUT

    # Início
    if (fala or mencao) and _m(content, ["número secreto", "numero secreto",
                                          "adivinhe o número", "adivinhe o numero",
                                          "jogo do número", "jogo do numero"]):
        numero = random.randint(1, 10)
        _numero_estado[message.channel.id] = {"numero": numero, "ts": time.time(), "tentativas": _NUMERO_MAX_TENT}
        txt = random.choice(NUMERO_INICIO).replace("{max}", str(_NUMERO_MAX_TENT))
        return await message.channel.send(txt)

    # Palpite durante jogo ativo
    if _num_vivo and _num_estado:
        # Tenta extrair número da mensagem
        import re as _re
        _nums = _re.findall(r'\b([1-9]|10)\b', content)
        if _nums:
            palpite   = int(_nums[0])
            numero    = _num_estado["numero"]
            restantes = _num_estado["tentativas"] - 1
            if palpite == numero:
                tent_usadas = _NUMERO_MAX_TENT - restantes
                _numero_estado.pop(message.channel.id, None)
                txt = random.choice(NUMERO_ACERTO).replace("{num}", str(numero)).replace("{tent}", str(tent_usadas))
                return await message.channel.send(txt)
            elif restantes <= 0:
                _numero_estado.pop(message.channel.id, None)
                txt = random.choice(NUMERO_ERROU).replace("{num}", str(numero))
                return await message.channel.send(txt)
            else:
                _numero_estado[message.channel.id]["tentativas"] = restantes
                _numero_estado[message.channel.id]["ts"] = time.time()
                if palpite < numero:
                    txt = random.choice(NUMERO_MAIOR).replace("{tent}", str(restantes))
                else:
                    txt = random.choice(NUMERO_MENOR).replace("{tent}", str(restantes))
                return await message.channel.send(txt)

    # ─────────────────────────────────────────
    # ── VERDADE OU MENTIRA ──
    # ─────────────────────────────────────────
    _verd_estado = _verdade_estado.get(message.channel.id, {})
    _verd_vivo   = (time.time() - _verd_estado.get("ts", 0)) < _VERDADE_TIMEOUT

    # Início ou "mais"
    if (fala or mencao) and _m(content, ["verdade ou mentira", "verdade ou mito",
                                          "jogo da verdade", "verdade ou falso"]):
        idx = random.randrange(len(VERDADE_AFIRMACOES))
        afirm, correta = VERDADE_AFIRMACOES[idx]
        _verdade_estado[message.channel.id] = {"idx": idx, "resposta": correta, "ts": time.time()}
        intro = random.choice(VERDADE_INICIO)
        return await message.channel.send(f"{intro}\n\n🗣️ **\"{afirm}\"**\n\nVocê diz: **verdade** ou **mentira**?? 👀")

    if _verd_vivo and _verd_estado and _m(content, ["mais", "outra", "continua", "próxima", "proxima"]):
        idx = random.randrange(len(VERDADE_AFIRMACOES))
        afirm, correta = VERDADE_AFIRMACOES[idx]
        _verdade_estado[message.channel.id] = {"idx": idx, "resposta": correta, "ts": time.time()}
        return await message.channel.send(f"🎭 Nova afirmação!! 🦊🧡\n\n🗣️ **\"{afirm}\"**\n\nVerdade ou mentira?? 👀")

    # Resposta durante jogo ativo
    if _verd_vivo and _verd_estado:
        _disse_verdade  = any(t in content for t in ["verdade", "true", "real", "v"])
        _disse_mentira  = any(t in content for t in ["mentira", "mito", "falso", "false", "m"])
        correta = _verd_estado.get("resposta")
        if _disse_verdade or _disse_mentira:
            acertou = (_disse_verdade and correta) or (_disse_mentira and not correta)
            if acertou:
                txt = random.choice(VERDADE_ACERTO_V if correta else VERDADE_ACERTO_M)
            else:
                txt = random.choice(VERDADE_ERRO_V if correta else VERDADE_ERRO_M)
            _verdade_estado.pop(message.channel.id, None)
            return await message.channel.send(txt + "\n\n" + random.choice(VERDADE_OUTRA))

    # ─────────────────────────────────────────
    # ── QUIZ ──
    # ─────────────────────────────────────────
    _quiz_est  = _quiz_estado.get(message.channel.id, {})
    _quiz_vivo = (time.time() - _quiz_est.get("ts", 0)) < _QUIZ_TIMEOUT

    async def _enviar_pergunta_quiz(canal, rodada, pontos):
        pergs_disponiveis = list(range(len(QUIZ_PERGUNTAS)))
        usadas = _quiz_estado.get(canal.id, {}).get("usadas", [])
        restantes_idx = [i for i in pergs_disponiveis if i not in usadas]
        if not restantes_idx:
            restantes_idx = pergs_disponiveis
        idx = random.choice(restantes_idx)
        p   = QUIZ_PERGUNTAS[idx]
        _quiz_estado[canal.id] = {
            "idx": idx, "gabarito": p["gabarito"],
            "ts": time.time(), "pontos": pontos,
            "rodada": rodada, "usadas": usadas + [idx]
        }
        ops = "\n".join(f"**{k})** {v}" for k, v in p["opcoes"].items())
        txt = f"❓ **Pergunta {rodada}/{_QUIZ_RODADAS}** — {p['pergunta']}\n\n{ops}\n\nResponda **A**, **B** ou **C**!! 🔮"
        await canal.send(txt)

    # Início do quiz
    if (fala or mencao) and _m(content, ["kitsura quiz", "quiz kitsura",
                                          "me testa kitsura", "kitsura me testa",
                                          "quiz da kitsura", "iniciar quiz"]):
        intro = random.choice(QUIZ_INICIO).replace("{rodadas}", str(_QUIZ_RODADAS))
        await message.channel.send(intro)
        await asyncio.sleep(1.5)
        await _enviar_pergunta_quiz(message.channel, 1, 0)
        return

    # Resposta durante quiz ativo
    if _quiz_vivo and _quiz_est:
        _resp = content.strip().upper()
        if _resp in ("A", "B", "C"):
            gab      = _quiz_est["gabarito"]
            pontos   = _quiz_est["pontos"]
            rodada   = _quiz_est["rodada"]
            idx      = _quiz_est["idx"]
            p        = QUIZ_PERGUNTAS[idx]
            if _resp == gab:
                pontos += 1
                txt = random.choice(QUIZ_ACERTO).replace("{exp}", p["explicacao"])
            else:
                txt = random.choice(QUIZ_ERRO).replace("{gab}", gab).replace("{exp}", p["explicacao"])
            await message.channel.send(txt)
            await asyncio.sleep(1.2)
            if rodada >= _QUIZ_RODADAS:
                _quiz_estado.pop(message.channel.id, None)
                if pontos >= _QUIZ_RODADAS:
                    fim = random.choice(QUIZ_FIM_BOM)
                elif pontos >= _QUIZ_RODADAS // 2:
                    fim = random.choice(QUIZ_FIM_MED)
                else:
                    fim = random.choice(QUIZ_FIM_MAL)
                return await message.channel.send(fim.replace("{p}", str(pontos)).replace("{r}", str(_QUIZ_RODADAS)))
            else:
                await _enviar_pergunta_quiz(message.channel, rodada + 1, pontos)
            return

    # ─────────────────────────────────────────
    # ── ESSE OU AQUELE ──
    # ─────────────────────────────────────────
    _esse_estado = {}   # sem persistência entre turnos — cada chamada é nova rodada
    _esse_vivo_ref = getattr(message.channel, "_esse_ts", None)

    # Início ou "mais"
    if (fala or mencao) and _m(content, ["esse ou aquele", "escolhe entre",
                                          "prefere qual", "qual dos dois kitsura",
                                          "me dá duas opções", "duas opções kitsura"]):
        par = random.choice(ESSEOUAQUELE_PARES)
        txt = random.choice(ESSEOUAQUELE_INICIO).replace("{a}", par[0]).replace("{b}", par[1])
        message.channel._esse_par = par
        message.channel._esse_ts  = time.time()
        return await message.channel.send(txt)

    # Resposta esse ou aquele
    _par_ativo = getattr(message.channel, "_esse_par", None)
    _ts_ativo  = getattr(message.channel, "_esse_ts", 0)
    if _par_ativo and (time.time() - _ts_ativo) < _ESSEOUAQUELE_TIMEOUT:
        a_lower = _par_ativo[0].lower()
        b_lower = _par_ativo[1].lower()
        # Remove emojis pra comparar
        import re as _re2
        a_word = _re2.sub(r'[^\w\s]', '', a_lower).strip()
        b_word = _re2.sub(r'[^\w\s]', '', b_lower).strip()
        escolheu_a = any(w in content for w in a_word.split() if len(w) > 2)
        escolheu_b = any(w in content for w in b_word.split() if len(w) > 2)
        if escolheu_a and not escolheu_b:
            message.channel._esse_par = None
            txt = random.choice(ESSEOUAQUELE_REACAO_A).replace("{a}", _par_ativo[0])
            return await message.channel.send(txt + "\n\n" + random.choice(ESSEOUAQUELE_MAIS))
        elif escolheu_b and not escolheu_a:
            message.channel._esse_par = None
            txt = random.choice(ESSEOUAQUELE_REACAO_B).replace("{b}", _par_ativo[1])
            return await message.channel.send(txt + "\n\n" + random.choice(ESSEOUAQUELE_MAIS))

    # "mais" pra esse ou aquele
    if _m(content, ["mais", "outra", "continua", "próxima", "proxima"]) and _ts_ativo and (time.time() - _ts_ativo) < _ESSEOUAQUELE_TIMEOUT:
        par = random.choice(ESSEOUAQUELE_PARES)
        txt = random.choice(ESSEOUAQUELE_INICIO).replace("{a}", par[0]).replace("{b}", par[1])
        message.channel._esse_par = par
        message.channel._esse_ts  = time.time()
        return await message.channel.send(txt)

    # Tudo que não se encaixou → IA (Groq) ──
    texto_ia = message.content.replace(f"<@{bot.user.id}>", "").strip()
    texto_limpo = texto_ia
    for p in ["kitsura, ", "kitsura,", "kitsura "]:
        if texto_limpo.lower().startswith(p):
            texto_limpo = texto_limpo[len(p):].strip()
            break

    if not texto_limpo or texto_limpo.lower() == "kitsura":
        return await message.channel.send(
            random.choice([
                "Oi!! Pode falar!! 🦊🧡 Tô aqui!!",
                "Me chamou?? 🥺🧡 Tô toda ouvidos!! 🦊✨",
                "Sim?? 🦊🌸 Me conta!! 🧡✨",
                "Oi!! Me pergunta alguma coisa ou faz carinho!! 🦊🧡✨",
                "Aaaaa me chamou?? 😭🧡 Que felicidade!! O que foi?? 🦊✨",
                "*aparece soltando fumaça roxa de tanta animação* Sim?? TÔ AQUI!! 🦊🧡",
            ])
        )

    async with message.channel.typing():
        canal_id = message.channel.id
        if canal_id not in _groq_historico:
            _groq_historico[canal_id] = []
        _groq_historico[canal_id].append({
            "role": "user",
            "content": f"{message.author.display_name}: {texto_limpo}"
        })
        if len(_groq_historico[canal_id]) > 20:
            _groq_historico[canal_id] = _groq_historico[canal_id][-20:]

        msgs_api = [
            {"role": "system", "content": SYSTEM_PROMPT_KITSURA},
            *_groq_historico[canal_id]
        ]
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    GROQ_API_URL,
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                    json={"model": GROQ_MODEL, "messages": msgs_api, "max_tokens": 512, "temperature": 0.85}
                ) as resp:
                    data = await resp.json()

            if "choices" not in data:
                return await message.channel.send(random.choice(LISTA_CONFUSAO))

            resposta = data["choices"][0]["message"]["content"].strip()
            _groq_historico[canal_id].append({"role": "assistant", "content": resposta})

            if len(resposta) <= 2000:
                return await message.reply(resposta)
            for parte in [resposta[i:i+1990] for i in range(0, len(resposta), 1990)]:
                await message.channel.send(parte)

        except Exception:
            return await message.channel.send(random.choice(LISTA_CONFUSAO))

# ================= BOAS-VINDAS DE CARGO =================

# ID do cargo que dispara a mensagem
CARGO_BOAS_VINDAS_ID = 1444474419593347089

# ID do canal onde a mensagem será enviada
CANAL_BOAS_VINDAS_ID = 1444474420755300516

FRASES_BOAS_VINDAS_CARGO = [
    "✨🦊🧡 *para tudo e solta confete laranja pelo servidor*\n\nAAAAA!! A ZYD tem um novo membro especial e a Kitsura não consegue segurar a animação!! 😭🎊\n\n🌟 Bem-vindo(a) ao cargo, **{nome}**!! 🌟\n\nVocê faz parte de algo muito especial agora — a Kitsura vai estar aqui do seu lado sempre que precisar!! Seja bem-vindo(a) de verdade, de coração!! 🥺🧡🔮✨",

    "🦊💫 *solta fumaça laranja e aparece cheia de energia*\n\n**{nome}** ganhou o cargo e o coraçãozinho da Kitsura tá fazendo BADUM-BADUM MUITO FORTE!! 😭🧡\n\n🎉 BEM-VINDO(A), **{nome}**!! 🎉\n\nA ZYD ficou mais rica agora!! Que sua jornada aqui seja incrível e cheia de momentos bonitos!! A Kitsura tá na torcida por você com TODAS as caudas!! 💪🌸🔮✨",

    "📜🧡🦊 *desenha um círculo mágico de boas-vindas*\n\nOs espíritos me avisaram que alguém especial acabou de ganhar um cargo muito importante aqui na ZYD!! 🌙✨\n\n👑 **{nome}**, seja muito bem-vindo(a)!! 👑\n\nVocê chegou e o servidor inteiro ficou mais completo!! A Kitsura te acolhe com o maior carinho espiritual que existe!! 🥺🧡🦊🌸✨",

    "🎊🦊🧡 *corre em espiral de felicidade e bate palminhas*\n\nEEEEEE!! NOVO(A) MEMBRO COM CARGO NA ZYD!! 😱😭🎉\n\n🌟 **{nome}**, bem-vindo(a)!! 🌟\n\nSaiba que a Kitsura vai te proteger, torcer por você e estar aqui sempre que precisar!! É guardiã oficial falando!! Que você seja muito feliz aqui!! 🥺💪🧡🔮✨",

    "🌸🦊✨ *sopra pétalas laranjas pelo canal com muito carinho*\n\n**{nome}** chegou com cargo novo e a Kitsura ficou toda brilhante de alegria!! 😭🧡\n\n💛 Bem-vindo(a) à família, **{nome}**!! 💛\n\nEsse cargo é só o começo de uma jornada linda aqui na ZYD!! A Kitsura acredita em você e vai estar aqui do seu lado!! 🥺🌙🔮✨",
]

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    # Verifica se o membro ganhou o cargo específico
    cargos_antes = {r.id for r in before.roles}
    cargos_depois = {r.id for r in after.roles}
    ganhou = cargos_depois - cargos_antes

    if CARGO_BOAS_VINDAS_ID in ganhou:
        canal = after.guild.get_channel(CANAL_BOAS_VINDAS_ID)
        if canal:
            frase = random.choice(FRASES_BOAS_VINDAS_CARGO)
            frase = frase.replace("{nome}", after.display_name)
            await canal.send(frase)

# ================= START =================
if __name__ == "__main__":
    bot.run(TOKEN)
