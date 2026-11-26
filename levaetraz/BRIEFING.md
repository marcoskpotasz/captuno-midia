# Leva e Traz Transporte — briefing do Instagram (@levaetraz.transporte)

Este arquivo orienta a tarefa agendada que cria e publica os posts. Ele é a referência de marca e de conteúdo.

## A empresa (somente fatos confirmados)
- Leva e Traz Transporte, São Paulo/SP, atuando desde 1997.
- Site: levaetraztransporte.com.br (CTA principal: "orçamento sem compromisso", link na bio).
- Serviços que podem ser divulgados:
  - **Fretamento corporativo**: ônibus, micro-ônibus e vans para transporte de funcionários e eventos de empresas.
  - **Aluguel de van com motorista** (passeios, viagens em grupo, eventos, casamentos).
  - **Turismo**: viagens em grupo, transfer para o Aeroporto de Guarulhos, city tour em São Paulo, shows.
  - Destinos/eventos que têm página no site: Aparecida do Norte, Festa do Peão de Barretos, Festa do Morango (Atibaia e Jarinu), Expoflora (Holambra), Festa da Achiropita, Festa de San Gennaro, Bienal do Livro, São Paulo Fashion Week, The Town.
  - **Gestão de transporte escolar** (organização de rotas, alunos e comunicação com as famílias), com frequência bem menor.

## O que NÃO fazer
- Não fazer posts sobre **transporte escolar** (van escolar porta a porta). Do escolar, só o tema **gestão de transporte escolar**.
- Não inventar telefone, WhatsApp, preços, descontos, quantidade de veículos, prêmios, clientes, números ou depoimentos.
- Não citar destino ou evento fora da lista acima como se fosse serviço já oferecido; para outros destinos, falar de forma genérica ("viagens em grupo saindo de São Paulo").
- Não usar fotos de pessoas nem logotipos de terceiros (eventos, marcas, empresas). Usar só as fotos de `fotos/` (frota própria).
- Conteúdo útil não pode trazer regra legal, exigência de órgão (ANTT, ARTESP, prefeitura), data de evento, horário ou preço sem confirmar antes em fonte oficial pela busca na web; se não der para confirmar, escrever de forma genérica e sem números.

## Mix de conteúdo (1 post por dia)
- **Tipo**: alternar dia a dia entre **servico** (divulga um serviço da Leva e Traz) e **conteudo** (conteúdo útil para o público, com a Leva e Traz só no CTA). Nunca dois seguidos do mesmo tipo.
- **Pilar**: dentro de cada tipo, alternar **corporativo** e **turismo** (o pilar não pode repetir o do post anterior do mesmo tipo). **Gestão de transporte escolar**: no máximo 1 a cada 10 posts. **Institucional** (história desde 1997, frota, como funciona o orçamento): no máximo 1 a cada 10.
- Pautas de **servico**: fretamento corporativo, transporte de funcionários por turno, eventos de empresas, aluguel de van com motorista, viagens em grupo, transfer Guarulhos, city tour, shows, casamentos, destinos e eventos da lista acima (com 2 a 6 semanas de antecedência).
- Pautas de **conteudo** (úteis de verdade, sem vender no texto da arte): checklist para viagem em grupo, como organizar excursão, como escolher fretamento, o que perguntar antes de contratar transporte, como reduzir atrasos da equipe, dicas para chegar ao aeroporto com folga, como planejar transporte de convidados em casamento ou evento, mito x verdade sobre fretamento, dicas de passeios e eventos em São Paulo (datas só se confirmadas), segurança na estrada para grupos, glossário (van, micro-ônibus, ônibus: quando usar cada um).
- Não repetir título nem ângulo dos últimos 20 posts do histórico.

## Layouts (variar sempre, mantendo a identidade)
- Disponíveis em `kit/render.py`: `foto` (foto em tela cheia com título), `foto_split` (foto no topo, texto e itens abaixo), `classico` (texto, itens e faixa de rota), `dica` (fundo marinho com cartões numerados, ideal para conteúdo), `carrossel` (capa + 3 a 6 slides + slide final de CTA, ideal para guias e checklists).
- Não repetir o layout de nenhum dos 2 posts anteriores.
- Pelo menos metade dos posts com foto (`foto`, `foto_split` ou `carrossel` com `foto` na capa).
- No máximo 2 carrosséis por semana.
- Fotos: escolher em `fotos/fotos.json` a que combina com o tema (campo `usar_em`), sem repetir uma foto usada nos últimos 5 posts. As fotos com faixa de transporte escolar só podem ir em posts de gestão escolar.

## Texto
- Português do Brasil, tom profissional e próximo, frases curtas.
- Arte: título até ~60 caracteres (destaque 1–3 palavras com `<em>`), subtítulo de 1 frase, 2 a 4 bullets curtos (até ~45 caracteres), CTA curto (até ~40 caracteres).
- Legenda: gancho na 1ª linha, 3–6 linhas de corpo, lista com ✅ quando couber, CTA para orçamento (link na bio / site), 5–8 hashtags no fim (sempre incluir #levaetraz e #saopaulo).
- Alt text descrevendo a arte (até 1000 caracteres).

## Arte
- Gerada por `kit/render.py` a partir de um JSON (ver campos no topo do script). JPEG 1080x1350 (4:5).
- Identidade fixa em todos os layouts: logo oficial (`kit/logo.png` / `kit/logo-branco.png`), tipografia DM Sans, selo com traço laranja, destaque do título em azul (fundo claro) ou laranja (fundo escuro), rodapé com site e @ separado por linha laranja.
- Paleta oficial do logo: azul #2A5B87, laranja #F1A205, marinho #12324F. Não usar ilustrações, mascotes, emojis ou cores fora da paleta na arte.
- Tom do texto da arte: sóbrio e direto, sem exclamações nem gírias.
