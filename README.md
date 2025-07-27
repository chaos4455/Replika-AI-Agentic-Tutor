<div align="center">

# 🎓 Estudo On-Demand: RAI Agentic Tutor 🧠

### Seu tutor pessoal com IA para aprendizado infinito e sob medida.


</div>

<div align="center">

![Status](https://img.shields.io/badge/status-em%20desenvolvimento%20ativo-green?style=for-the-badge)
![Versão](https://img.shields.io/badge/versão-7.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![Framework](https://img.shields.io/badge/Flask-WebApp-black?style=for-the-badge&logo=flask)
![IA](https://img.shields.io/badge/IA-Google%20Gemini-purple?style=for-the-badge&logo=google-gemini)
![Licença](https://img.shields.io/badge/licença-MIT-green?style=for-the-badge)

</div>

<p align="center">
  <em>Idealizado por <a href="https://www.linkedin.com/in/itilmgf/" target="_blank">Elias Andrade</a></em>
</p>

---

## 💡 A Visão: Por que o Estudo On-Demand foi criado?

No mundo atual, o conhecimento é a moeda mais valiosa. No entanto, o aprendizado tradicional muitas vezes é engessado, genérico e pouco motivador. Cursos online podem ser caros, livros podem ser densos e a curiosidade genuína sobre um tópico específico raramente é atendida com uma ferramenta prática e imediata.

Como **Arquiteto de Soluções de IA**, com experiência em criar Web Apps, Agentes Inteligentes, Co-pilots e explorar o vasto potencial de LLMs e NLP, eu me perguntei: **"E se pudéssemos criar um tutor pessoal que materializa o conhecimento instantaneamente, de forma gamificada e verdadeiramente instrutiva?"**

O **Estudo On-Demand** é a resposta a essa pergunta. Ele não é apenas um gerador de quizzes; é um protótipo de um ecossistema de aprendizado dinâmico. A ideia central é democratizar a educação, permitindo que qualquer pessoa, em qualquer lugar, possa transformar sua curiosidade em uma experiência de aprendizado interativa, eficaz e, acima de tudo, divertida. Este projeto é a fusão da minha paixão por tecnologia, educação e o poder transformador da Inteligência Artificial Generativa.

---

## ✨ O que ele faz? A Experiência de Aprendizagem

Este aplicativo web transforma um simples tópico em uma aula completa e interativa, simulando a experiência de aplicativos de aprendizado de idiomas como o Duolingo, mas com um universo infinito de assuntos.

*   **🧠 Geração de Conteúdo Inteligente:** Utilizando o poder do **Google Gemini 1.5 Flash**, a aplicação gera de 20 a 30 perguntas relevantes e desafiadoras sobre qualquer tema que você imaginar.
*   **🎓 Explicações que Ensinam:** O verdadeiro aprendizado não está em acertar, mas em entender o porquê. Cada resposta correta vem acompanhada de uma **explicação técnica e didática** gerada pela IA, transformando cada questão em uma microaula.
*   **🎮 Interface Gamificada:** Com um sistema de vidas, barra de progresso, feedback instantâneo e uma pontuação final, a jornada de aprendizado se torna um jogo envolvente, incentivando o usuário a continuar e a se superar.
*   **📚 Biblioteca Pessoal de Aulas:** Todos os quizzes gerados são salvos automaticamente. Você pode revisitar suas aulas a qualquer momento, reforçando o conhecimento sem precisar gerar tudo novamente.
*   **⚙️ Aprendizado Flexível:** Prefere uma experiência mais relaxada? Ative o modo de **"Vidas Infinitas"** e explore o conteúdo sem a pressão de ser eliminado.

---

## 🚀 Como Começar: Use o Poder da IA em 3 Passos

Para que a mágica da IA aconteça, você precisa conectar o aplicativo ao cérebro dele: o Google Gemini. É mais simples do que parece!

### Passo 1: Obtenha sua Chave da API (API Key)

1.  Acesse o **[Google AI Studio](https://aistudio.google.com/)**.
2.  Faça login com sua conta Google.
3.  No painel esquerdo, clique em **"Get API key"**.
4.  Clique em **"Create API key in new project"**.
5.  Copie a chave gerada. Ela se parece com `AIzaSy...` e é o seu acesso pessoal à IA. **Guarde-a com segurança!**

### Passo 2: Configure a Chave no Projeto

1.  Abra o arquivo do projeto: `duolingo_on_demand_app_v7.py`.
2.  Logo no início do código, você encontrará um dicionário de configuração chamado `CONFIG`.
3.  Cole a sua chave da API no campo `"API_KEY"`, substituindo o valor existente.

    > **Exemplo (dentro do código):**
    > `...`
    > `"API_KEY": 'COLE_SUA_CHAVE_AQUI',`
    > `...`

### Passo 3: Execute e Aprenda!

Com a chave configurada, basta executar o script Python. O terminal irá mostrar o endereço local (como `http://127.0.0.1:8999`) para você acessar no seu navegador. Pronto! Seu tutor pessoal de IA está online e esperando seu primeiro comando.

---

## 🔮 A Visão para o Futuro (Roadmap)

A versão 7.0 é apenas o começo. Este projeto serve como base para um agente de aprendizado muito mais sofisticado. Os próximos passos na evolução do **RAI Agentic Tutor** incluem:

*   **🧠 Memória Permanente e Contextual:** O agente se lembrará de seus erros e acertos em diferentes tópicos, identificando suas áreas de fraqueza e sugerindo revisões personalizadas.
*   **🤖 Autoaprimoramento do Quiz:** A IA analisará a performance dos usuários nas questões, descartando as que são confusas ou pouco eficazes e gerando novas, em um ciclo de melhoria contínua.
*   **🏞️ Geração Multimodal:** Futuramente, os quizzes poderão incluir imagens, diagramas e até pequenos vídeos gerados por IA para explicar conceitos complexos de forma visual.
*   **🗺️ Trilhas de Aprendizagem Adaptativas:** Com base no seu desempenho, o agente poderá sugerir o próximo tópico a ser estudado, criando uma trilha de conhecimento coesa e personalizada para seus objetivos.
*   **🗣️ Interação por Voz e Agentes Conversacionais:** Transformar a experiência em um diálogo, onde você pode pedir explicações mais aprofundadas ou fazer perguntas de acompanhamento sobre as respostas.

---

## 👨‍💻 Sobre o Arquiteto

<img src="https://avatars.githubusercontent.com/u/7990529?v=4" width="100" align="left" style="margin-right: 20px; border-radius: 50%;">

Eu sou **Elias dos Santos de Andrade**, um Arquiteto de Soluções de IA e Desenvolvedor apaixonado por construir a ponte entre o potencial da Inteligência Artificial e aplicações práticas que resolvem problemas do mundo real.

Com uma forte bagagem em **LLMs, NLP, Web Apps, e na criação de Agentes e Co-pilots**, meu foco é projetar sistemas inteligentes que não sejam apenas funcionais, mas também intuitivos, éticos e que agreguem valor real à vida das pessoas. Este projeto é um reflexo dessa filosofia.

### 🔗 Conecte-se e Colabore

Estou sempre aberto a novas ideias, colaborações e discussões sobre o futuro da tecnologia. Vamos nos conectar!

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Elias%20Andrade-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/itilmgf/)
[![GitHub](https://img.shields.io/badge/GitHub-chaos4455-181717?style=for-the-badge&logo=github)](https://github.com/chaos4455)

---

## 📜 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes. Sinta-se à vontade para clonar, modificar e usar este projeto como base para suas próprias inovações.
