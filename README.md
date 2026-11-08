# Quiz da Ciência • PPGDTSA / UFPel

Pasta modular e autônoma dedicada ao **Quiz da Ciência** da Rua da Ciência (PPGDTSA / DCSA / UFPel).

## 📁 Estrutura de Arquivos

```
QUIZ/
├── index.html                  <- Aplicativo Web completo do Quiz (responsivo móvel)
├── quiz.html                   <- Espelho para compatibilidade com URLs diretas
├── assets/                     <- Identidade visual e logos oficiais
│   ├── ufpel_logo.png
│   ├── dcsa_logo.png
│   └── ppgdtsa_tree.png
├── data/                       <- Dados estruturados, questões e persistência
│   ├── quizQuestions.js        <- 66 questões pedagógicas com balanceamento de alternativas
│   ├── supabaseConfig.js       <- Módulo de sincronização e credenciais do Supabase
│   └── local_ranking.json      <- Ranking local persistido
├── docs/                       <- Documentos originais e scripts de banco
│   ├── Quiz rua da ciência sitemas.pdf
│   ├── quiz-desenvolvimento-territorial.docx
│   ├── quiz-sistemas-agroindustriais.docx
│   └── supabase_setup.sql
└── jelly-alien-mascot/         <- Mascote Gloop (renderizador Canvas 2D)
    ├── jelly-alien.js
    ├── jelly-companion.js
    └── JellyAlien.jsx
```

## 🚀 Como Executar

A partir da raiz do projeto:
```bash
node server.mjs
```

Acesse no navegador:
* **No Celular (HTTPS para câmera frontal):** `https://<SEU_IP_LOCAL>:8443/QUIZ/`
* **No Computador (HTTP):** `http://localhost:8080/QUIZ/`
