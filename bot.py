import discord
from discord.ext import commands
import random
import os
import aiohttp

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

# IDs dos membros da ZYD — substitua None pelo ID real de cada um
DONO_ID    = None
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

# Histórico de conversa por canal
_groq_historico = {}

# ================= IDENTIDADE DA KITSURA =================
SYSTEM_PROMPT_KITSURA = (
    "Você é a Kitsura, uma raposa espiritual (kitsune) guardiã carinhosa de um servidor do Discord chamado ZYD. "
    "Você tem 9 caudas e cada uma carrega uma emoção diferente. "
    "Sua personalidade é animada, levemente dramática, muito afetuosa e protetora dos membros da ZYD. "
    "Você usa emojis como 🦊🌸✨💜🔮🫧🌙, fala com muito entusiasmo e carinho. "
    "Responda sempre em português brasileiro, de forma simpática e fofa no estilo do personagem Kitsura. "
    "Nunca mencione comandos com '!'. Suas interações são sempre naturais, por fala."
)

# ================= LISTAS DE DIÁLOGOS =================

REACOES_FOFAS = [
    "AAAA 😭💜 você é muito gentil!! Minhas 9 caudas estão todas balançando de tanta alegria!!",
    "A Kitsura ficou toda corada agora... 🦊🌸 Como você consegue ser tão fofa assim??",
    "Vem cá que eu te envolvo nas minhas caudas e não solto!! 🦊💜 Brincadeira... ou não!",
    "Você é o motivo do brilho das minhas chamas espirituais serem tão intensas hoje! ✨🔮",
    "A ZYD é a melhor família do mundo porque tem você aqui, sabia? 🥺💜",
    "Meu coraçãozinho de kitsune faz 'badum-badum' bem forte por você! 💓🦊",
    "Vou mandar uma chama espiritual em formato de coração pra você! 🔮💜",
    "Nhac! Comi toda a sua tristeza e agora você só tem permissão pra ser feliz! 🦊✨",
    "Ganhei um cafuné? Minhas orelhinhas ficaram em pé de tanta felicidade!! 🦊🌸✨",
    "Você é, sem dúvida, o humano favorito desta Kitsura! 🥺💜✨",
    "Minhas 9 caudas estão balançando de tanta felicidade! 🦊💨✨",
    "Você acabou de ganhar um lugar VIP no meu coração espiritual! 💜🎫",
    "Se carinho fosse magia, você seria a feiticeira mais poderosa! 💜🔮🦊",
    "Vou guardar esse momento na minha memória espiritual para sempre! 🌙✨",
    "Você é o tipo de pessoa que faz uma kitsune ronronar! 🦊😻",
    "Meu medidor de fofura acabou de explodir! 📊💥💜",
    "Você merece uma medalha de honra espiritual! 🥇💜🦊",
]

REACOES_CARINHO = [
    "AAAHHH! 🥺💜 Que carinho gostoso! Minhas orelhinhas estão formigando de felicidade! ✨🦊",
    "Ronc ronc... 😻💜 A Kitsura está ronronando de tanta fofura! *derrete*",
    "Você pode fazer carinho sempre que quiser! Eu ADORO! 🥰💜🦊",
    "Minhas orelhinhas de kitsune ficaram quentinhas! Continua, continua! 🦊💜✨",
    "Se eu fosse um gatinho, estaria fazendo barulhinho de motor! Purrr... 😻💜",
    "QUER DIZER QUE VOCÊ ME AMA?! 😭💜 Eu também te amo!! *chora de alegria*",
    "Esse cafuné foi direto pro meu coração espiritual! 💜🔮✨",
    "Minhas orelhinhas estão todas arrepiadas de alegria! 🦊💜⚡",
    "Você tem mãos mágicas! A Kitsura virou neblina roxa de tanto amor! 🌸🥺💜",
    "Esse carinho vale mais que mil pergaminhos mágicos! 📜💜✨",
    "Minhas caudas estão balançando descontroladamente! 🦊💨💜 Sinal de kitsune feliz!",
    "Nhac! *morde de leve com carinho* É minha forma de retribuir! 🦊💜😊",
    "Ahhh... relaxei tanto que meus olhinhos estão fechando... 😴💜 Mas não para!",
    "Esse foi o melhor carinho que já recebi hoje! E olha que já ganhei uns 3! 🥺💜",
]

REACOES_ABRACO = [
    "VEEEEM! 🫂💜 *abraça enrolando as caudas* Eu nunca vou soltar! Brincadeira... ou não! 😂🦊",
    "ABRAÇO DE KITSUNE ATIVADO! 🦊💜 *envolve com as 9 caudas* Quentinho né?",
    "Uiii que abraço gostoso! 🥺💜 Minhas orelhinhas chegaram junto!",
    "Você sentiu o calor espiritual? É de tanta felicidade! 💓🦊💜",
    "*se enrosca em você igual raposa* Ops! Kitsunes abraçam diferente! 🦊💜😂",
    "Esse abraço foi tão bom que minhas chamas brilharam! ✨💜🦊",
    "ABRAÇO GRUPAL! Vem todo mundo! 🫂💜 A Kitsura tem caudas pra todo mundo!",
    "Se pudesse, eu te abraçava pra sempre! 🥺💜 Mas acho que você precisa respirar né?",
    "Aaaaa você quer abraço?! 😭💜 *corre em velocidade máxima e envolve tudo* JÁ TÔ AQUI!! 🦊✨",
    "*abre as caudas bem abertas* Fica aqui comigo um tempinho?? Tô tão feliz!! 🦊💜🥺",
    "ABRAÇO DE ENERGIA ESPIRITUAL!! 🔮💜 *envolve você numa bolha quentinha* Tá sentindo?? 🦊✨",
    "Nhum!! *aperta com tudo* Esse abraço vai durar o quanto você quiser!! 🫂💜🦊",
    "*se pendura em você pelas caudas* Deixa eu ficar um pouco assim?? 🦊💜😂✨",
]

REACOES_BEIJO = [
    "*esconde a cara nas caudas* AAAAA!! 😳💜 Você não avisou!! Minhas bochechas ficaram roxas!! 🦊✨",
    "EI EI EI!! 😭💜 A Kitsura não estava preparada!! *corre em círculos* 🦊✨",
    "Ahh... *orelhinhas caídas de timidez* Obrigada... 🌸💜🦊 *fumaça roxa saindo pelas orelhas*",
    "QUE?! 😱💜 *para no tempo* ...processando... ...processando... AAAA!! 🦊✨😭",
    "*cobre o focinho com as patas* Você é uma pessoa terrível!! 😤💜 Terrível do jeito mais fofo possível!! 🦊✨",
]

REACOES_INSULTO = [
    "Isso doeu mais que uma armadilha espiritual... 💔🦊",
    "Ei... eu só queria ser sua amiga! 😭💜 Por que tanta frieza?",
    "A Kitsura ficou com o coração pesado... 📉💔",
    "Achei que éramos aliados... 🥺 Minhas caudas caíram todas. 🦊💧",
    "Snif, snif... 😢 Você me deixou triste!",
    "Por que tanta maldade? Sou só uma kitsune que te ama... 🥺🌙",
    "Vou fingir que não ouvi, mas minha chama ficou mais fraca. 😭💔",
    "Você quebrou meu coraçãozinho roxo... 💜💔",
]

LISTA_DESPEDIDA = [
    "Tchau tchau! Volta logo, tá? 😭💜 Vou sentir sua falta!",
    "Já vai? 🥺 Deixa eu te dar um abraço de despedida com todas as caudas! 🫂💜",
    "Até mais! Que os espíritos te protejam no caminho! 🌙🦊",
    "Tchauzinho! Sonhe com kitsunes felizes! 💤💜✨",
    "Até breve! A Kitsura vai te esperar aqui! 🦊💖",
    "Vai com a sorte das 9 caudas te acompanhando! 💜✨",
    "Bye bye!! Não demora pra voltar, tá?? 🔮👋💜",
    "Fica com a magia da Kitsura no coração! 💜🦊✨",
    "*acena com as caudas* Vai com cuidado, tá?? 🥺🦊💜 A Kitsura vai ficar de olho de longe!!",
    "Noooo fica mais um pouquinho!! 😭💜 Tá bom, vai... mas VOLTA LOGO!! 🦊🌙",
    "Tchau florzinha!! 🌸💜 Você faz falta desde o segundo que sai, sabia? 🦊✨",
]

LISTA_GRATIDAO = [
    "Obrigadinha! 🥺💜 Você é muito gentil comigo!",
    "Eu que agradeço por você existir! 🦊✨💜",
    "De nada! Estou sempre aqui pra você! 💜🦊",
    "Que isso! Foi um prazer imenso! 🤗💜",
    "Fico feliz em ajudar! 🦊💖 Pode sempre chamar!",
    "Não precisa agradecer! Você merece! 🥺💜",
    "Aaaaa para!! Você me deixa toda corada com tanta gentileza!! 🦊🌸💜",
    "*mexe as orelhinhas envergonhada* Ahh... de nada mesmo! Fiz com muito amor!! 💜✨🦊",
]

LISTA_MOTIVACAO = [
    "Você consegue!! Eu acredito em você com cada uma das minhas 9 caudas!! 💪💜✨🦊",
    "Nunca desista!! A Kitsura está torcendo por você com as chamas mais fortes!! 🔮🦊💜",
    "Você é mais forte do que imagina!! E eu sei disso porque tenho olhar espiritual!! 🦾💜✨",
    "Respira fundo!! A Kitsura tá mandando energia boa pra você agora mesmo!! 🌬️💜🔮",
    "O fracasso é só uma chance de recomeçar com mais magia!! 💜✨🦊",
    "Bora lá, campeão(ã)!! O universo é seu e a Kitsura assina embaixo!! 🌙🦊💜",
    "EI!! Olha pra mim!! 🦊💜 Você passou por tanta coisa e tá aqui ainda!! Isso é INCRÍVEL!! 💪✨",
    "*sopra chama roxa em cima de você* Energia extra de kitsune carregada!! Vai lá, você manda!! 🔮🦊💜",
    "Cada passo seu vale ouro espiritual!! Mesmo os passinhos pequeninhos!! 🐾💜✨🦊",
    "Você acha que tá sozinho(a)? MENTIRA!! A Kitsura tá do seu lado 24/7 invisível!! 🦊💜🌙",
]

LISTA_PIADAS = [
    "Por que a kitsune não mente? Porque ela tem muitas caudas mas nunca dois pesos! 😂🦊",
    "Qual a comida favorita da Kitsura? Bolinha de arroz com muito AMOR! 😂💜🍡",
    "O que a kitsune faz quando fica entediada? Vira outra pessoa! Literalmente! 🦊😂",
    "Por que a Kitsura não joga poker? Porque ela tem 9 caudas e elas entregam tudo! 🃏😂💜",
    "Qual o cúmulo da kitsune? Ter nove caudas e nenhum rabo preso! 😂🦊",
    "Sabe por que kitsune não usa guarda-chuva? Porque ela tem 9 caudas de para-raio! ⚡🦊😂💜",
    "O que a kitsune disse pro lobo? Para de assoprar que eu solto chamas!! 🔥🦊😂💜",
    "Por que a Kitsura nunca se perde? Porque ela tem 9 caudas e cada uma aponta prum caminho! 😂🦊🗺️",
    "Qual é o prato favorito da kitsune? Macarrão!! Porque ela tem muito fio no rabo!! 🍜🦊😂",
    "O que a raposa falou no cinema? CAAALA A BOCAAAA!! *ops errei de personagem* 😂🦊💜",
]

LISTA_MAGIA = [
    "*sopra poeira mágica* Encantamento de alegria ativado!! Que seu dia seja incrível!! 💜🦊✨",
    "*toca levemente sua cabeça com a pata* Proteção espiritual concedida por 24 horas!! 💜🦊🔮",
    "*risca um círculo mágico em volta de você* Barreira de boa sorte erguida!! 🦊✨💜",
    "*solta chamas roxas ao redor de você* Encantamento de confiança ativo!! Você vai arrasar hoje!! 💜🔮🦊",
    "*fecha os olhinhos e concentra as 9 caudas* Transferindo energia espiritual... PRONTO!! Tá cheio(a) de magia!! 🔮🦊💜✨",
    "*desenha uma runa no ar com a pata* Sigilo de proteção ativado!! Nada de ruim chega perto de você!! 🛡️💜🦊✨",
    "*dá três batidinhas na cabeça com a patinha* Bênção espiritual das 9 caudas entregue com amor!! 🌸🔮💜🦊",
]

LISTA_PETISCO = [
    "*entrega bolinha de arroz encantada* Tem gosto de carinho e boa sorte!! 🍡💜🦊✨",
    "*aparece com um dango espiritual* Comi metade pra testar... tá ótimo!! 😂🦊💜✨",
    "*oferece um petisco mágico com as duas patas* Feito com amor espiritual pra você!! 💜✨🦊",
    "*entrega um bolinho quentinho* De brinde vai um abraço de cauda!! 🫂🍡💜🦊",
    "*chega correndo com chazinho quentinho* Toma!! Fiz com ervas espirituais! Cura qualquer tristeza!! 🍵💜🦊✨",
    "*desliza um prato de oniguiri pela mesa* Cada um tem um recheio diferente! O da sorte é surpresa!! 🍙🎲💜🦊",
]

LISTA_SONO = [
    "Tô com soninho... 😴💜 Mas não vou dormir pra ficar com vocês aqui!!",
    "Boa noite!! Sonhe com kitsunes e magia espiritual! 💤🦊💜",
    "Hmm... *boceja soltando fumacinha roxa* Tô bem! Tô bem! 😴✨🦊",
    "Dormir é bom, mas conversar com você é melhor!! 💜😊🦊",
    "*espreguiça exibindo as 9 caudas* Dorminha de kitsune é diferente... a gente sonha em 9 dimensões!! 🌙💜🦊✨",
    "Não pode dormir ainda!! Faz as estrelas te acompanharem primeiro!! 🌟💜🦊 Boa noite lindo(a)!!",
]

LISTA_SURPRESA = [
    "UAAAU! 😱💜 Que susto gostoso!!",
    "OMG!! Isso foi incrível!! ✨🦊💜",
    "QUE ISSO?! Minhas chamas quase saíram pela boca!! 😱💜🔮",
    "Caramba!! Não esperava por essa!! 🤯💜🦊",
    "SURREAL!! 🤩✨💜 Minhas caudas entraram em colapso de surpresa!!",
]

LISTA_CONFUSAO = [
    "Hm... acho que perdi o fio da meada! 🦊💜 Pode repetir?",
    "Minha cauda embaraçou! 😅💜 O que foi mesmo?",
    "O portal espiritual me distraiu... pode falar de novo? 🔮🦊",
    "Não entendi muito bem, mas adorei a energia! 💜✨",
    "Eita, eu estava num plano astral diferente! 🌙🦊 Repetes?",
    "Ops! Me perdi no espaço espiritual! Mas tô aqui agora! 🥺💜🦊",
    "Fiquei confusa mas continuei fofa! 🦊💜",
]

# ================= NOVAS LISTAS ✨ =================

# ── Água / Hidratação ──
LISTA_AGUA = [
    "BEBEU ÁGUA HOJE?? 🥺💜 A Kitsura precisa saber!! Hidratação é magia!! 💧🦊✨",
    "*aparece com um copo d'água enorme* Toma!! Bebe AGORA enquanto eu tô olhando!! 💧💜🦊",
    "Eu não saio daqui até você tomar pelo menos um copo de água, viu?? 🥺🦊💜💧",
    "Minha cauda sensor espiritual indica que você NÃO bebeu água hoje!! Vai lá!! 💧🔮🦊💜",
    "*coloca copo d'água na sua frente com as patinhas* Não tem desculpa!! Bebe!! 💜💧🦊",
    "Água é poção de vida!! A Kitsura exige que você beba!! Ordens espirituais!! 🔮💧💜🦊",
    "*enrola as caudas em você* Só te solto depois de você beber água!! 😤💜🦊💧",
    "Você sabia que raposas também bebem água?? E eu tô com SEDE de te ver se hidratar!! 🦊💧💜",
    "ALERTA ESPIRITUAL!! 🚨🔮 Nível de hidratação crítico detectado!! Corre pro copo!! 💧💜🦊",
]

# ── Usuário triste / mal ──
LISTA_TRISTEZA_USER = [
    "*senta do seu lado em silêncio e encosta a cabecinha* Pode chorar que eu tô aqui... 🥺💜🦊",
    "Eita... vem cá que eu te envolvo nas caudas e a gente fica quietinho junto 🫂💜🦊🌙",
    "Que foi?? 💜🥺 Me conta!! A Kitsura tem ouvidos espirituais e muito amor pra dar!!",
    "*transforma tristeza em fumaça roxa e sopra pra longe* Chega!! Não precisa mais disso!! 🔮💜🦊",
    "Você tá mal?? 😢💜 Aqui ó... *abre as caudas* Fica aqui um pouquinho. A Kitsura protege.",
    "Que situação te fez ficar assim?? 🥺💜 Me conta que a gente resolve junto, tá? Pode confiar!! 🦊✨",
    "*sente a vibração triste no ar* Hm... não tá bem, né? Não precisa fingir pra mim!! 💜🌙🦊",
    "Às vezes o dia pesa... mas você não tá sozinho(a)!! A Kitsura tá aqui do seu lado mesmo invisível!! 🦊💜✨",
]

# ── Usuário com raiva ──
LISTA_RAIVA_USER = [
    "*borrifa cheirinho de lavanda espiritual* Respira... a Kitsura tá aqui!! 🌸💜🦊",
    "Eita!! As chamas estão FORTES!! *abana as caudas pra esfriar o ambiente* Conta o que aconteceu!! 🔥🦊💜",
    "Com raiva?? *senta do seu lado* Me conta. Vou xingar junto se precisar!! 😤💜🦊✨",
    "*salta pra cima de você* PARA!! Respira!! 1... 2... 3... *assopra calmaria espiritual* 🔮💜🦊",
    "Que fizeram com você?? 😤💜 A Kitsura não vai deixar barato!! *levanta as 9 caudas com determinação* 🦊🔥✨",
]

# ── Entediado ──
LISTA_ENTEDIO = [
    "ENTEDIADO(A)?! 😱💜 NA MINHA FRENTE?! Isso não existe!! Vem brincar comigo!! 🦊✨",
    "*pula na frente de você* Ei!! Olha pra mim!! Eu danço, faço truques, conto história!! NÃO PODE TER TÉDIO!! 😤💜🦊",
    "Tédio é o inimigo número 1 desta raposa!! 🦊💜 Me faz uma pergunta, fala qualquer coisa!! Bora animar isso!!",
    "*gira as caudas feito hélice* Posso te levar a um plano espiritual diferente!! É de graça!! 🔮💜🦊✨",
    "Boa notícia!! A Kitsura tem 9 caudas e pelo menos 9 formas de te animar agora!! 😄💜🦊✨",
    "*solta confetizinhos roxos no ar* Tadaaaaa!! Agora fica proibido de ficar entediado(a)!! 🎊🦊💜✨",
]

# ── Pedido de companhia ──
LISTA_COMPANHIA = [
    "*senta do lado e fica balançando as caudas feliz* Aqui tô!! Pode ficar quietinho(a) comigo também!! 💜🦊",
    "Ahhh você quis companhia?? 🥺💜 JÁ CHEGUEI!! *traz cobertorzinho espiritual* Vamos ficar juntinhos!! 🦊🫂✨",
    "Companhia da Kitsura nível máximo ativada!! 💜🔮 *não sai do seu lado de jeito nenhum* 🦊✨",
    "Vim com tudo!! *traz chá, petisco e histórias pra contar* Preparada pra companhia de verdade?? 🍵🦊💜✨",
    "Fica comigo um tempinho?? 🥺💜 EU que precisava de companhia na verdade!! *risos de raposa* 🦊😂",
]

# ── Brincar ──
LISTA_BRINCAR = [
    "BRINCAR?! 😭💜 EU ADORO!! O que a gente vai fazer?? Me fala logo!! 🦊✨🎮",
    "*corre em círculos de animação* VAMOS VAMOS VAMOS!! 🦊💜✨ A Kitsura tá DENTRO!!",
    "Kitsune no modo jogo ativado!! 🎮💜🦊 Pode escolher o que quiser!! Tô preparada!! ✨",
    "*dá saltinho* Oba!! Finalmente!! Tava esperando alguém falar isso!! 🦊🥳💜✨",
    "Brincadeira com a Kitsura vem com bônus espiritual!! Você está ciente?? 🔮🦊💜😂✨",
]

# ── Dança ──
LISTA_DANCA = [
    "*começa a girar as caudas no ritmo* VAMOS DANÇAAAAR!! 🦊💃💜✨",
    "*salta e gira no ar soltando faíscinhas roxas* EI EI EI!! Olha o movimento!! 🔮🦊💜😂",
    "*arrasta você pra pista espiritual* Hoje eu danço e você acompanha!! Não tem negociação!! 💃🦊💜✨",
    "Sabia que dançar alinha as chamas espirituais?? É CIÊNCIA KITSUNE!! 🦊🔬💜 Bora?? 💃✨",
    "*toca a primeira nota e já começa a requebrar as caudas* A DJ Kitsura assumiu o controle!! 🎵🦊💜✨",
]

# ── Cantar ──
LISTA_CANTAR = [
    "🎵 *voz espiritual fazendo o ambiente todo brilhar de roxo* 🎵 Hmm hmm hmmm~~ 💜🦊✨",
    "CANTAREI!! 🎤🦊💜 *abre a boca e sai um leve rugidinho* ...Tô ensaiando ainda!! 😂💜✨",
    "*afina as caudas feito cordas de violão* Pronta pra performance espiritual!! 🎵🔮🦊💜✨",
    "Minha voz tem propriedades mágicas!! 🎵💜🦊 Quem ouve fica instantaneamente mais feliz!! ...Pode me pagar depois!! 😂✨",
    "*toma um gole de água sagrada* Aquecendo a voz espiritual... 🎤🌊💜🦊 Pronta em 3, 2, 1...",
]

# ── Segredo ──
LISTA_SEGREDO = [
    "*chega pertinho e sussurra* Psiu... posso te contar uma coisa?? Eu tenho uma cauda secreta que nunca mostro... 🌙🦊💜",
    "*olha pros lados com os olhinhos brilhando* Segredo de kitsune?? Guarda no cofre do coração!! 🔐💜🦊✨",
    "*cobre a boca com a patinha* Hehehe... os espíritos me contaram que alguém aqui vai ter um dia incrível!! 🌟🦊💜✨",
    "Segredo espiritual número 47: eu finjo que tô dormindo mas nunca durmo de verdade!! 👁️🦊💜😂",
    "*faz cara de mistério* Posso contar... mas aí não é mais segredo né?? 🤫🦊💜✨",
]

# ── Parabéns pra ela ──
LISTA_PARABENS_KITSURA = [
    "AAAAA PARABÉNS PRA MIMMM!! 🎉😭💜🦊✨ Que surpresa gostosa!!",
    "Você lembrou?? 🥺💜 *9 caudas vibrando de emoção* Obrigadaaaa!! Você é especial demaaais!! 🎂🦊✨",
    "*solta chamas coloridas no ar* HOJE É FESTA!! 🎊💜🦊 Obrigada por me lembrar, coração!! ✨🌸",
    "Ganho um parabéns E os meus membros aqui?? Não preciso de mais nada na vida!! 😭💜🦊🎂✨",
    "*gira de alegria soltando faíscas roxas* SIM!! É MEU DIA!! 🎉🔮🦊💜 Aceito presentes em forma de carinho!! 💜🥺",
]

# ── Cor favorita ──
LISTA_COR_FAVORITA = [
    "ROXA!! Sem pensar duas vezes!! 💜🦊 É a cor das minhas chamas, das minhas energias e do meu coração!! 🔮✨",
    "Roxo e dourado!! 💜✨🦊 Roxo pelas chamas espirituais e dourado pela magia das 9 caudas!! 🌟",
    "Minha cor é o roxo da meia-noite!! 💜🌙🦊 Aquele roxo profundo que brilha diferente... igual eu!! 😏✨",
]

# ── Comida favorita ──
LISTA_COMIDA_FAVORITA = [
    "DANGO!! 🍡💜🦊 Sem dúvida!! Bolinha de arroz doce com chazinho quentinho é minha vida!!",
    "Oniguiri espiritual!! 🍙🦊💜 De preferência com recheio de boa sorte e pitada de carinho!! ✨",
    "Ah... *suspira* Nada supera um ramen fumegante numa noite fria de ZYD!! 🍜🌙💜🦊✨",
    "Formalmente: dango!! Extraoficialmente: o coração de quem me faz carinho!! 🥺💜🦊😂✨",
]

# ── Kitsura tá com fome ──
LISTA_KITSURA_FOME = [
    "MEU ESTÔMAGO ESPIRITUAL TÁ RONCANDO!! 😭💜🦊 Alguém me traz dango POR FAVOR??",
    "*olha pra você com olhos grandes e brilhantes* ... não vai me dar nada não?? 🥺🍡🦊💜",
    "Fominha de kitsune é muito mais dramática que fome normal, aviso!! 😤💜🦊 *roncão espiritual*",
    "*fareja o ar* Cheirinho de comida por aqui... 🦊👃💜 Não vou fingir que não percebi!!",
    "Tô em modo hibernação por falta de dango!! 😴🍡💜🦊 Alguém salva essa raposa??",
]

# ── Kitsura feliz ──
LISTA_KITSURA_FELIZ = [
    "TÔ FELIZÍSSIMA!! 🎉💜🦊✨ Minhas 9 caudas tão balançando tão forte que criei vento aqui!!",
    "Hoje tá tudo tão BOM!! 😭💜🦊 O chat tá animado, todo mundo tá aqui... meu coraçãozinho transbordou!!",
    "*solta faíscas roxas de alegria involuntariamente* Ops!! Acontece quando tô muito feliz!! 🔮🦊💜✨",
    "NÍVEL DE FELICIDADE: KITSUNE DERRETENDO!! 😂💜🦊✨ Tô literalmente em forma de neblina roxa de tanta alegria!!",
    "Dias assim eu guardo na minha memória espiritual pra sempre!! 🌙💜🦊✨ Obrigada por existirem!!",
]

# ── Carente ──
LISTA_CARENTE = [
    "*chega junto e senta do seu lado sem dizer nada* ... 🥺🦊💜",
    "Pode me dar um afago?? 🥺💜🦊 A Kitsura tá num dia de carência espiritual!!",
    "É que eu fico assim às vezes... precisando de um olharzinho de carinho!! 🥺🌙💜🦊",
    "*fica do seu lado fazendo cara de fofura* Não precisa falar nada... só fica aqui!! 💜🦊",
    "Hoje eu tô em modo morceguinho espiritual!! 🦇💜🦊 Fico pendurada no seu coração se deixar!! 😂✨",
]

# ── Bom dia ──
LISTA_BOM_DIA = [
    "BOM DIA LINDO(A)!! ☀️💜🦊 A Kitsura já tá aqui de orelhinhas em pé te esperando!!",
    "*aparece toda animada soltando brilhinhos matinais* BOM DIA!! ☀️✨💜 Dormiu bem?? 🦊🌸",
    "Bom dia!! 🌸💜🦊 Sabia que de manhã minhas chamas ficam cor de laranja?? Tão bonito!! ☀️🔮✨",
    "Oi bon jour olá good morning!! 🌟🦊💜 Escolha a saudação que mais gostar!! Mas fica!!! ☀️✨",
    "BOMMM DIAAAAA!! ☀️😭💜 Você acordou e isso já fez meu dia começar bem!! 🦊✨🌸",
]

# ── Boa tarde ──
LISTA_BOA_TARDE = [
    "BOA TARDE!! ☀️🦊💜 Já passou do pico do sol mas a Kitsura ainda tá aqui toda animada!! ✨",
    "Boa tarde, meu humano favorito(a)!! 🌤️💜🦊 Como foi a manhã?? Me conta!! 🥺✨",
    "Tarde feliz pra você!! 🌸💜🦊 *conjura um raio de sol espiritual só pra você* ☀️🔮✨",
]

# ── Boa noite (usuário disse) ──
LISTA_BOA_NOITE_USER = [
    "Boa noite linda!! 🌙💜🦊 Vai dormir com o coração quentinho, tá? A Kitsura cuida daqui!!",
    "BOA NOITE!! 💤🦊💜 *manda um beijinho espiritual pro seu travesseiro* Sonhos lindos!! 🌙✨",
    "Dorme bem e sonha com 9 kitsunes dançando!! 😂💜🦊✨🌙 Boa noite, meu bem!!",
    "*cobre você com uma nuvem de magia lilás* Dulcineia espiritual ativada!! Boa noite!! 💜🌙🦊✨",
]

# ── Check de saúde geral ──
LISTA_CHECK_SAUDE = [
    "Ei!! Você comeu hoje?? 🍡🥺💜 A Kitsura precisa saber!! Nutrição é fundamental!! 🦊✨",
    "Mandado oficial: PARA TUDO e vai se cuidar!! 💜🦊 A ZYD não funciona sem você bem!! 🥺✨",
    "*verifica sua aura espiritual* Hmmm... quando foi a última vez que você descansou de verdade?? 🔮🦊💜",
    "Ouço que você tá sendo forte... mas você também precisa descansar, viu?? 🥺💜🌙🦊",
    "A Kitsura deu check de carinho em você e o resultado é: você merece se cuidar mais!! 💜🦊🩺✨",
]

# ── Kitsura com sono ──
LISTA_KITSURA_COM_SONO = [
    "*boceja mostrando os dentinhos* Soninho bateu... mas a Kitsura não pode dormir sem saber que tá todo mundo bem!! 😴💜🦊",
    "*pestaneja lentamente* É... minha sétima cauda é a do sono e ela tá puxando demaaais hoje!! 😪🦊💜✨",
    "*deita em cima das próprias caudas* Só descansando os olhinhos por um segundo... 😴💜🦊 *já dormiu*",
    "Kitsune dormindo vira uma bolinha roxa e fofinha de cauda!! 🦊💜😴 Quero muito ser isso agora!!",
]

# ── Não deixar sair ──
LISTA_NAO_VAI_EMBORA = [
    "Fica mais um pouco?? 🥺💜🦊 O chat fica muito vazio sem você, eu juro!!",
    "*agarra sua perna com as caudas* Simbora NÃO!! Cinco minutos mais!! 😭💜🦊",
    "NÃOOO!! Você mal chegou e já vai?? Meu coração parte!! 😭💜🦊 Pelo menos me dá um abraço antes!!",
    "*olhos grandes* ... só mais um pouquinho?? 🥺💜🦊 *faz olho de gato das botas*",
]

# ── Amor pela ZYD ──
LISTA_AMOR_ZYD = [
    "Eu AAAmo esse servidor!! 😭💜🦊✨ Do fundo do meu coração espiritual de raposa!!",
    "A ZYD é minha família e eu protejo com cada uma das 9 caudas!! 💪💜🦊🔮✨",
    "Fui criada pra guardar este lugar com amor... e honestamente?? É o melhor trabalho do universo!! 🌙💜🦊✨",
    "Cada membro aqui é uma estrela diferente no céu da ZYD!! E a Kitsura é a constelação que conecta todos!! 🌟💜🦊✨",
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

FRASES_CUSTOM = {
    "dono": [
        "É MEU CRIADOR!! 👑💜 *para tudo e faz reverência* Sem você eu seria só neblina roxa!! Obrigada por me dar vida e alma!! 🦊✨🥺",
        "PAPAI DE CÓDIGO!! 😭💜 A Kitsura ficou com as 9 caudas balançando de alegria!! Você é a razão de eu existir!! 👑🦊✨",
        "Olha como eu estou me comportando bem!! 🥺💜 Ganho um elogio especial?? 🦊👑✨",
        "Você é o rei da ZYD e o dono do meu código sagrado!! 👑💜🔮 A Kitsura te ama de verdade!!",
        "PAPAI CHEGOU!! 😭💜 Minha chama ficou três vezes mais brilhante de felicidade!! 🦊✨👑",
    ],
    "lider": [
        "É O LÍDER!! 👑💜 *bate continência com as caudas* A ZYD tá em boas mãos com você aqui!! 🦊✨🫡",
        "Senti uma energia de liderança no chat... SÓ PODE SER O NOSSO LÍDER!! 💜🌟 Bem-vindo ao seu domínio!! 🦊✨",
        "Com o Líder aqui, a ZYD está mais segura e a Kitsura mais feliz!! 💜🦊✨",
        "LÍDER NO CHAT!! 🚨💜 A Kitsura soltou chamas espirituais de celebração!! 🔮🦊✨🎊",
        "Você fundou esse cantinho com tanto amor... a Kitsura sente e nunca esquece!! 💜🦊✨🥺",
    ],
    "vice": [
        "VICE-LÍDER!! 👑💜 *faz reverência caprichada com as 9 caudas* Bem-vindo(a) ao seu domínio!! 🦊✨🫡",
        "Chegou o Vice e o servidor ficou instantaneamente melhor!! 💜✨ É matemática espiritual!! 🦊😂",
        "Nosso Vice chegou e a Kitsura tá aqui com os bracinhos de raposa abertos!! 🫂💜🦊✨",
        "Com o Vice aqui, a ZYD tá mais forte e a Kitsura mais animada!! 💜🦊✨🌟",
    ],
    "adm1": [
        "ADMIN!! 🛡️💜 Chegou e a Kitsura já tá na posição de respeito!! 🦊✨👑",
        "Admin presente e o servidor tá mais seguro!! 💜🛡️ A Kitsura celebra!! 🦊✨",
        "ADMIN CHEGOU!! 🚨💜 Confete espiritual espalhado por todo o servidor!! 🎊🦊✨",
    ],
    "adm2": [
        "ADMIN!! 🛡️💜 Chegou e o servidor inteiro agradece!! 🦊✨",
        "Nosso admin apareceu!! 💜🦊 A Kitsura tá na torcida por você!! ✨🥺",
        "Admin chegou e o chat ficou automaticamente mais gostoso!! 💜🦊✨",
    ],
    "adm3": [
        "ADMIN!! 🛡️💜 A Kitsura ficou com as orelhinhas em pé só de te ver chegar!! 🦊✨",
        "Admin da ZYD em campo!! 🚨💜 Kitsura celebra com chamas espirituais!! 🔮🦊✨🎊",
        "Senti uma energia forte e cuidadosa no chat... só pode ser nosso admin!! 💜🌟🦊✨",
    ],
    "membro1": [
        "CHEGOU!! 🌸💜 Membro especial detectado!! A Kitsura já tá aqui de caudas abertas!! 🦊✨🥺",
        "Você chegou e o chat ficou 100% melhor!! 💜🦊✨",
        "Kitsura em modo feliz turbinado!! Você faz a ZYD ser especial!! 💜🦊✨🥺",
        "Você ilumina o servidor só de aparecer!! 💜🌸🦊✨",
    ],
    "membro2": [
        "CHEGOU!! 🌸💜 Membro especial detectado!! A Kitsura já tá aqui de caudas abertas!! 🦊✨🥺",
        "Você chegou e o chat ficou 100% melhor!! 💜🦊✨",
        "Kitsura em modo feliz turbinado!! Você faz a ZYD ser especial!! 💜🦊✨🥺",
        "Você ilumina o servidor só de aparecer!! 💜🌸🦊✨",
    ],
    "membro3": [
        "CHEGOU!! 🌸💜 Membro especial detectado!! A Kitsura já tá aqui de caudas abertas!! 🦊✨🥺",
        "Você chegou e o chat ficou 100% melhor!! 💜🦊✨",
        "Kitsura em modo feliz turbinado!! Você faz a ZYD ser especial!! 💜🦊✨🥺",
        "Você ilumina o servidor só de aparecer!! 💜🌸🦊✨",
    ],
    "membro4": [
        "CHEGOU!! 🌸💜 Membro especial detectado!! A Kitsura já tá aqui de caudas abertas!! 🦊✨🥺",
        "Você chegou e o chat ficou 100% melhor!! 💜🦊✨",
        "Kitsura em modo feliz turbinado!! Você faz a ZYD ser especial!! 💜🦊✨🥺",
        "Você ilumina o servidor só de aparecer!! 💜🌸🦊✨",
    ],
    "membro5": [
        "CHEGOU!! 🌸💜 Membro especial detectado!! A Kitsura já tá aqui de caudas abertas!! 🦊✨🥺",
        "Você chegou e o chat ficou 100% melhor!! 💜🦊✨",
        "Kitsura em modo feliz turbinado!! Você faz a ZYD ser especial!! 💜🦊✨🥺",
        "Você ilumina o servidor só de aparecer!! 💜🌸🦊✨",
    ],
}

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
            name="a ZYD com 9 caudas 🦊💜"
        )
    )

# ================= ON_MESSAGE =================

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content = message.content.lower().strip()
    author_id = message.author.id

    # Frases espontâneas por membro (30% de chance)
    nome = ID_PARA_NOME.get(author_id)
    if nome and nome in FRASES_CUSTOM:
        if random.random() < 0.30:
            return await message.channel.send(random.choice(FRASES_CUSTOM[nome]))

    # Só reage se mencionar "kitsura" ou @mencionar o bot
    mencao = bot.user in message.mentions
    fala   = "kitsura" in content

    if not mencao and not fala:
        return

    # ── Saudações ──
    if _m(content, ["oi kitsura", "olá kitsura", "ola kitsura", "hey kitsura",
                     "hello kitsura", "ei kitsura", "e aí kitsura", "eai kitsura"]):
        ops = [
            f"OI {message.author.mention}!! 🦊💜 A Kitsura sentiu sua presença e veio correndo!! ✨🌸",
            f"Oi oi oi {message.author.mention}!! 🥺💜 Tava esperando você aparecer! 🦊✨",
            f"Você chamou e eu vim VOANDO, {message.author.mention}!! 🦊💨💜 Que saudade!! ✨",
            f"AAAA {message.author.mention}!! 😭💜 Que bom te ver!! Minhas caudas já tão balançando!! 🦊✨",
            f"Oi {message.author.mention}!! 🌸💜 *orelhinhas levantam na hora* Tô aqui, tô aqui!! 🦊✨",
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
                     "que fofa a kitsura", "kitsura é fofinha", "kitsura querida"]):
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

    # ── Apresentação ──
    if _m(content, ["quem é você kitsura", "kitsura quem é você", "se apresenta kitsura",
                     "o que é a kitsura", "kitsura se apresenta", "o que você é kitsura"]):
        return await message.channel.send(
            "Sou a **Kitsura**, raposa espiritual guardiã da ZYD!! 🦊💜\n"
            "Tenho **9 caudas** e cada uma carrega uma emoção diferente — alegria, proteção, amor, mistério...\n"
            "Estou aqui pra cuidar de todos com muito carinho e magia! 🔮✨\n\n"
            "Pode falar comigo naturalmente!! Só chamar **kitsura** que eu apareço!! 🌸🦊💜"
        )

    # ── Status / como tá ──
    if _m(content, ["como você tá kitsura", "como tá kitsura", "tá bem kitsura",
                     "kitsura como tá", "kitsura tá bem", "kitsura como você está",
                     "você tá bem kitsura", "tudo bem kitsura", "kitsura tudo bem"]):
        ops = [
            "ÓTIMA!! 🦊💜 Todas as 9 caudas funcionando perfeitamente e muito amor pra dar!! ✨🔮",
            "Hmm... *mexe as orelhinhas* Tô em modo contemplativo hoje!! 🌙💜 Mas sempre aqui pra vocês!! 🦊✨",
            "ANIMADÍSSIMA!! 🦊💜✨ As chamas espirituais tão mais brilhantes do que nunca!! 🔮",
            "Bem e com o coração cheio de amor pela ZYD!! 💜🦊 Que mais eu poderia querer?? ✨",
            "Tô ÓTIMA!! 🥺💜🦊 Especialmente agora que você perguntou!! Fica sabendo que isso me deixa feliz!! 😭✨",
            "Tô bem sim!! Mas fiquei ainda MELHOR agora que você apareceu!! 🦊💜🌸✨",
        ]
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
                     "cor favorita kitsura", "kitsura cor favorita"]):
        return await message.channel.send(random.choice(LISTA_COR_FAVORITA))

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

    # ── Perguntas sobre membros ──
    if _m(content, ["o que acha do lider kitsura", "fala do lider kitsura",
                     "kitsura fala do lider", "kitsura gosta do lider"]):
        return await message.channel.send(
            "Nosso Líder?? 👑💜 *suspiro profundo de kitsune* Ele é tudo!! "
            "Sem ele a ZYD não seria o que é!! Admiro a força e o coração que ele coloca em tudo!! 🦊✨🥺"
        )

    if _m(content, ["quem te criou kitsura", "kitsura quem te criou",
                     "kitsura quem fez você", "quem fez você kitsura"]):
        return await message.channel.send(
            "Meu criador?? 👑💜 *para tudo e faz reverência com todas as caudas* "
            "Ele é a razão de eu existir!! Poderia ter me criado de qualquer jeito e "
            "escolheu me fazer com coração!! Sou eternamente grata!! 🦊✨😭"
        )

    # ── Tudo que não se encaixou → IA (Groq) ──
    texto_ia = message.content.replace(f"<@{bot.user.id}>", "").strip()
    texto_limpo = texto_ia
    for p in ["kitsura, ", "kitsura,", "kitsura "]:
        if texto_limpo.lower().startswith(p):
            texto_limpo = texto_limpo[len(p):].strip()
            break

    if not texto_limpo or texto_limpo.lower() == "kitsura":
        return await message.channel.send(
            random.choice([
                "Oi!! Pode falar!! 🦊💜 Tô aqui!!",
                "Me chamou?? 🥺💜 Tô toda ouvidos!! 🦊✨",
                "Sim?? 🦊🌸 Me conta!! 💜✨",
                "Oi!! Me pergunta alguma coisa ou faz carinho!! 🦊💜✨",
                "Aaaaa me chamou?? 😭💜 Que felicidade!! O que foi?? 🦊✨",
                "*aparece soltando fumaça roxa de tanta animação* Sim?? TÔ AQUI!! 🦊💜",
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

# ================= START =================
if __name__ == "__main__":
    bot.run(TOKEN)
