---
title: "The Layers of AI experience"
source_url: "https://emilycampbell.co/writing/layers-of-ai-experience"
author: "Emily Campbell"
published_date: "2026-06-03"
---

# The Layers of AI experience

*Designing beneath the surface*

*21 MIN READ*

It's hard to imagine that it has been only 3 ½ years since ChatGPT was released to the public. We're still so early in the process of understanding how this generative material works, how it incorporates into tasks and journeys, and how it changes what we build and for whom.

What is clear though, is we are entering a renaissance of new design roles and opportunities for design influence.

The introduction of generative AI into digital products has upended the interaction model that anchored much of the previous era of design. Great AI products are multi-dimensional. Small changes to one can have an outsized impact on the whole.

### The Layers of AIUX

*The model below explores how design can influence each of these layers individually, and how they work together to collectively shape the final product's experience.*

1. **User interfaces** — Where people direct and oversee the AI's behavior
2. **Context** — What the system knows and infers about the user
3. **Harness** — Structure that determines what the model can access, use, and do
4. **Model** — Training, capabilities, and behavior that shape how the model itself reasons
5. **Governance** — Rules, standards, or preferences that set the AI's parameters
6. **Emergence** — Variance and unknown behavior, revealed through use

Spare me the "design is dead" takes. Design is more important than ever. However, the form of our roles and work is evolving, just as it has before, to meet the new challenges and opportunities presented by our changing medium.

## Past is prologue

*The concept of design as a multi-layered domain is not new. What is changing is how complex the system is as a whole, and how deep into the system design can influence.*

### Deterministic design

In the early web, work was often segmented by role. Visual designers owned website UIs; information architects owned site navigation and structure; business stakeholders owned requirements; etc. This reflected the waterfall nature of product development, and often led to workflows where each discipline optimized for their own area of focus rather than the outcomes of the product as a whole.

In 2000, Jesse James Garrett published his seminal essay, *[The Elements of User Experience](http://www.jjg.net/elements/)*, describing an alternative model. He explored how websites were actually composed of multiple planes, each dependent on the others. For example, navigation reflected product strategy, while usability issues in the interface might reveal weaknesses in the underlying architecture.

Myopic optimization ultimately harmed the user experience. Garrett argued that designers needed to understand the experience produced by the system as a whole, rather than limiting their responsibility or influence to the layer they directly controlled:

> The user experience development process is all about ensuring that no aspect of the user's experience with your site happens without your conscious, explicit intent. This means taking into account every possibility of every action the user is likely to take and understanding the user's expectations at every step of the way through that process
>
> — Jesse James Garrett, *The Elements of User Experience*

The result was a highly deterministic model of design, where the team was responsible for understanding the user's goals, mapping their journeys, and coordinating decisions across all five planes in order to intentionally shape the final product.

### Anticipatory design

*Jesse James Garrett, [The Elements of User Experience](http://www.jjg.net/elements/) (2000)*

Twenty years later, Jamie Mill revisited this framework as *[The Elements of Product Design](https://jamiemill.com/blog/2021-07-10-elements-of-product-design/)*.

As products became more algorithmic and adaptive to user data and behavior, it became more difficult to design for every possible use case.

Mill's updated model applied a wider lens and considered the many influences that shape the user experience. Beyond the "solution space" of the product itself, Garrett's original focus, Mill also considered the "problem space", where discovery practices reveal user needs and behavior, as well as "the real world," accounting for constraints, incentives, and existing mental models that shape how the product is understood and used.

This new interpretation reflected an evolution in how we understood the role of design, and who participates in it. Mill recognized that many of the facets that influence how people use and value a product are managed by decisions made outside of the design team, and that product design therefore needed to account for a wider domain of ownership.

This presents product design as more explicitly outcome-oriented than strictly deterministic. The work of design is not merely to define the final delivery, but to anticipate the less predictable conditions around it and facilitate a process that leads to better outcomes for users.

The contribution of both Garrett and Mill is that they made the dimensionality of good design tangible. Garrett showed that designers needed to extend their focus beyond the layer of the product they controlled. Mill extended that responsibility beyond the product itself, showing that experience design is also shaped by the user's context, the product's domain, and the broader system in which it operates.

### Probabilistic design and AI experience

*Jamie Mill, [The Elements of Product Design](https://jamiemill.com/blog/2021-07-10-elements-of-product-design/), reinterpreting Garrett's model to fit the wider lens of Product Design*

With the advent of generative AI, product systems have become more complex. In some ways, this is an extension of algorithmic products, which already introduced dynamic, personalized experiences. But with AI systems it is no longer only the algorithm that introduces variability; the underlying model itself is probabilistic, creating behaviors and emergent patterns that cannot always be reduced to explicit rules, states, or predefined paths.

As a result, every interaction within these products may include traces of decisions, biases, references, and dependencies from the model, its training data, and its available tools, plus any outside context introduced into the interaction.

We cannot control for every outcome directly through the interface, but we can design the conditions that shape a model's generation. In that regard, the work of design looks less like specifying every expected state, as Garrett's model encouraged, and instead closer resembles system design, identifying and manipulating the [leverage points in a system](https://donellameadows.org/archives/leverage-points-places-to-intervene-in-a-system/)[^1] that exist in the layers below the surface.

### We need full-stack designers

I do not mean that term in the traditional, engineering sense. Designers don't need to be machine learning engineers, policy experts, or model researchers to build effective AI products. It does mean we need to be multilingual, able to fluently discuss how each layer beneath the interface impacts the user experience, and how to intervene when necessary.

Garrett asked designers to look beyond the surface layer they controlled. Mill asked designers to look beyond the product and into the conditions that shaped how it was understood and used. AI asks designers to go one layer deeper again: into the model, the harness, the context, the policies, and the emergent behaviors that produce the experience before it ever reaches the interface.

*Emily Campbell, [The Layers of AI Experience](/layers-of-ai-experience.pdf), the author's model for probabilistic design*

## The layers of AI UX

AI experience is composed of a set of highly interdependent layers that collectively shape how a product behaves. As the user interacts with the system, each layer may change in form and purpose. Early on, interactions depend heavily on direct instruction from the user. Over time, however, the system takes over, managing the user's needs through its context of the problem, running independent, constrained by its harness, governing model, and user oversight.

By understanding how each component influences the end experience, designers can better locate where interventions will be most effective at delivering value, supporting human needs, and making the system more legible, accountable, and safe.

### The User Interface layer

AI design discourse is still heavily weighted toward the surface, exploring the dynamics of chat interfaces along with familiar and novel patterns that connect generative interactions with heuristics and paradigms.

This isn't surprising. The interface is where most people first encounter AI, and generative systems often require an initial input before an interaction can begin.

User interfaces are not going to disappear, but their role changes the deeper into a session a user progresses, supporting the system rather than driving it. It's likely we'll see their function and form continue to evolve with the rise of agentic systems, wearables, and other non-traditional products.

Early in the user journey, AI requires ***direction*** from people, guiding its goals, constraints, and other instructions. Users may provide this through, [workflows](https://www.shapeof.ai/patterns/chained-action?utm_source=emilycampbell.co), [inline actions](https://www.shapeof.ai/patterns/inline-action?utm_source=emilycampbell.co), [connected services](https://www.shapeof.ai/patterns/connectors?utm_source=emilycampbell.co), and other inputs.

We've taken to calling these prompts, but prompting is really only one surface for instructing the model. Inline actions, ambient nudges, and user-defined workflows offer a palette of alternatives. A product that relies strictly on prompts has a ceiling for engagement, since it's inefficient (and annoying) to write long, specific, context-rich instructions with every turn.

In any case, we expect AI products to build context about us over time so they can anticipate our needs rather than wait to be told. The faster a model accurately grasps the user's intent, the faster the system becomes an augmenting utility. When this sub-surface system is working well, the model can act with more autonomy, and the purpose of the interface leans toward ***oversight***, allowing the user to manage and orchestrate the model without requiring constant intervention.

While traditional systems focus onboarding and early interactions on helping the user learn the product, introducing more advanced features through progressive disclosure as the journey progresses, onboarding into AI products looks less like people learning how to use the system, and more like the system learning how to interpret the user. The better the system's understanding of the person, the less complication needs to appear in the interface. We're moving towards progressive autonomy.

This is why the debate about AI interfaces cannot be reduced to whether chat is a good or bad surface to anchor on. The right interface depends on the context surrounding the interaction, like how familiar the user is with the domain, how much the AI knows about them, how sensitive the situation is, and how much confidence the system has in its response.

As that context changes, the interface may need to evolve as well, even for similar touchpoints. The same task for the same user might require direct instruction early on, but eventually could be served through an autonomous backend process guarded by evals once the system had earned the user's trust.

Chat can still be an effective surface for this, and should not be discounted, but it's not a stable state. Interfaces may instead begin to resemble instrument panels, allowing direct inputs but not requiring it.

Interface design is therefore becoming less about choosing a single pattern for the use case and more about matching the surface to the state of the relationship between the user and the model at any given time. Behind the scenes, designers need to consider the artifacts an agent may use for shared interactions; the evaluation tools that track the model's accuracy and flag issues; and the surfaces where people can view and adjust memory, skills, and instructions.

### The Context layer

Below any AI interface sits the context that provides the model with clues about the user's intent, needs, constraints, and ecosystem.

A well-constructed context keeps an AI experience from having to start cold every time a person asks for help. It guides the system to reference what matters about the user, details about their task, plus any surrounding conditions without forcing the person to repeat themselves. We design it deliberately through context engineering, which helps determine what information should be collected or passed through across interactions.

In that sense, this layer operates as the engine for an AI-powered experience.

In early interactions, the user helps the model establish an understanding of them through ***explicit*** inputs, like descriptions of their goals and concerns, or through imported third-party content and data. Almost immediately, the system begins to generate ***inferred*** context from the person's behavioral patterns, integrated systems, historical interactions, and content, forming the foundation of a working context layer that it can use to interpret future requests.

Picture this like slowly exploring a map in a video game. At first most of the terrain is hidden, but as you move through it, the map begins to reveal its topography, its buildings, hazards, and boundaries, becoming more useful as you go.

Context works similarly, as the system learns how the user works and what they care about, plus how they prefer the system to interact with them. Gradually, as this surface reveals itself, the AI is able to work more proactively with less direct input from the user, reducing the need for constant instruction as the experience becomes more adaptive and personalized.

An agent should learn, for example, that I prefer certain meetings on Thursday afternoons, that John should usually be invited, that I like shorter drafts for executives, or that a support escalation should be handled with more caution than a routine status update.

But a system needs help knowing what context to keep and what to discard. Too much context, through long context windows and bloated memory files, burns through token budgets and can [degrade results](https://cs.stanford.edu/~nfliu/papers/lost-in-the-middle.arxiv2023.pdf), a failure commonly called [*context rot*](https://www.understandingai.org/p/context-rot-the-emerging-challenge). Too little or unmaintained context allows the system to become inconsistent, unpredictable, or dependent on constant user intervention.

Neither situation is good, and both become more serious when the system remembers personal details it should not have, forgets things it should know, or carries forward the wrong context from a user or session.

This problem becomes more consequential as agents take a more active role in driving workflows and interacting with data and content on a person's behalf. Designers need to consider the agent's experience as well: how it receives context, how it manages goals, when it collaborates with the user, and how visible its actions need to be for review.

The UI and Context layers therefore need to be designed in tight harmony, with consideration for both people and AI agents, how they interact with the user and each other, and how their individual workflows intersect across journeys.

### The Harness layer

As experiences become more headless, more of the product's work moves out of the visible interface and into context-aware, autonomous background processes. AI systems therefore require an operational layer around the model for processing information and coordinating their actions within defined constraints. This serves as the model's harness, enabling it to complete tasks independently while remaining governed by permissions and user preferences that promote security and more predictable outcomes.

It may seem like this layer is the domain of developer experience or application architecture, but model harnesses are increasingly part of the user experience as well. They shape what the system can know, what it can do, how consistently it behaves, and how much control users have over autonomous work.

In practice, this is the difference between an AI that you can chat with and one that operates as a true collaborator by finding and managing data, drafting responses, routing information, and coordinating actions in pursuit of a goal.

There's no singular form that a harness might take. It can be relatively simple, orchestrating a single agent's workflows. Or it can manage a more complex agentive orchestration, where a central agent within the harness deploys and oversees the work of multiple sub-agents in pursuit of a single outcome. In either case, the system is composed of multiple components, designed to coordinate capabilities, manage dependencies, and structure how work moves through the broader AI system.

***Connectors*** determine access rules for the model. People need visibility into what data the system has permission to view and manipulate, in what context, and under what conditions. They also need ways to observe access patterns over time and modify rules when needed. This can follow familiar permission patterns for microphone, camera, location, or contacts, where the reason for access is clear when the permission is requested.

However, connectors also introduce new UX concerns because access to third-party systems changes the model's context, bringing external content and data into interactions in ways people may not expect. Designers need to make these relationships visible so people understand not only what is connected, but how those connections shape outputs and ongoing behavior.

***Tools*** determine what actions AI can take within the data and context it has access to. These might include reading and writing emails, updating records, or triggering a workflow. If tool permissions are too loose, models can take actions that lead to unintended consequences downstream, which the user may not discover until after the fact. Conversely, if permissions are too restricted, it's difficult for the agent to perform advanced capabilities without constant user intervention. This may be useful early in the user journey, but over time may lead to missed expectations of performance.

The flexibility of tool use affects how much independence the user grants or expects from the model, which directly impacts the quality of outcomes the system can deliver through advanced use. Designers need to construct the product system so tool use is appropriate to the context and risk of the situation where it's called, calibrating autonomy over time, and surfacing more advanced functionality in a way that leads to engagement instead of mistrust.

***Skills*** provide models with reusable working knowledge, such as methods and rules for processing information, required formats and criteria, and overall task instructions. Designers may help determine which skills should be available out of the box, balancing functionality with comprehension. By mapping the journeys and services that underpin the AI interaction, designers can also help determine when to introduce new skills, and how to teach users to construct their own so they understand the downstream effects.

Since skills have an opinionated impact on the model's behavior and output, designers should ensure users have visibility and control over which skills are active, what assumptions they contain, and how they are likely to affect the model's results. When implemented gracefully, skills can help users feel empowered and in control. Otherwise, they can become confusing or overwhelming, particularly to earlier users who haven't learned the model well enough to understand how to manage it.

***Agents*** are autonomous systems that combine skills, tools, and data access, pointed at specific goals to produce outcomes with increasing independence and coordination. They work within loops of delegated responsibility, taking on tasks that extend beyond single interactions or isolated capabilities. Agentic UX is emerging as a discipline in itself because these systems often involve multiple coordinated processes operating across layers of autonomy, introducing new challenges around orchestration, oversight, and emergent behavior.

This increase in autonomy underpins the changes at the context and UI layers, as the user experience shifts from directing actions for a single model to supervising agentic systems. A good agent experience makes autonomous work feel orchestrated, allowing users to observe and interrupt the model when needed without requiring them to micromanage every step. Designers need to consider not only how users define goals and constraints, but also how agents coordinate actions, manage objectives, and maintain alignment across multiple surfaces.

Together, connectors, tools, skills, and agents form the operational surface of AI systems. They define the boundary between human intent and machine execution.

### The Model layer

When most people hear the word *model*, they typically think about recognizable flagship systems like GPT, Claude, Gemini, Grok, and others. To a lay user, these systems may appear interchangeable, but the landscape of AI models is far broader, covering small and large models; general-purpose or vertical; and open and proprietary options.

For designers, the point is that these differences aren't arbitrary or only technical. Each model carries distinct characteristics into the end product, like changes in tone or personality, tolerances for risk or ambiguity, general reliability, and other traits that could be good or bad depending on the circumstances. These differences persist across labs and providers, and between different models produced by the same entity.

Models are first and foremost a reflection of their ***training***, including the data, tuning, learned weights, and reinforcement methods used to shape their character. This in turn impacts what it knows by default, how it responds in different situations and contexts, what it avoids, and which assumptions it carries into each interaction. A model trained to focus on reasoning is a poor solution for fast-moving, low-risk environments where latency is costly, just as a faster model may produce a more fluid experience, but with less nuance or reliability. Understanding these differences helps designers anticipate how the end experience will shift depending on the model selected.

The training of each model also impacts its ***capabilities***, which define what a model is specifically designed to do. Depending on how it was built, a model may excel at reasoning or speed; it may perform better on certain tasks like writing, coding, tool use, or multimodal understanding; and it may therefore work better in conjunction with different tools and domains than others. Designers can influence task design, which determines the work that should be delegated to the model, what should stay with the user, and how the interface can narrow the task so the model can perform well.

A powerful model can still be a poor fit for a user's specific need if its capabilities don't match. Determining whether and how to offer users choices around model delegation is a sensitive aspect of the user experience. It's not reasonable to expect users to have a broad understanding of the model landscape in order to get good results, but pre-set modes and other parameters can disguise this level of control through the interface.

Alternatively, model ***behavior*** can be designed by defining these tradeoffs up front. A reasoning model can be configured to accept different effort levels, swapping depth and accuracy against latency and cost depending on the circumstances. Or, a creative model can be programmed to accept a different number of turns in its generation, where a smaller number might enable draft mode, giving users the ability to iterate while managing token spend. Latency, verbosity, confidence, refusal patterns, creativity, consistency, and reasoning depth are behaviors that can be tuned, contributing to the distinct feel of the product in use.

Because models are the primary material of AI products, designers require enough fluency around their attributes to reason about their tradeoffs. They do not need to train the models themselves, but the better they understand how models behave, the more effectively they can harness them for different tasks and ensure the product leverages their strengths and constrains their risks.

### The Governance layer

The first four layers describe how AI experiences are composed. The lower layers of governance and emergence shift the frame from composition to operation. These are often not owned by the product team, but they directly affect the conditions in which AI products are deployed and used.

Policies, regulations, standards, and preferences are all examples of outside forces that directly or indirectly govern the user experience. Each layer is affected in some form, from data retention preferences that impact context storage; to a company's philosophy reflecting in model behavior; to standards that determine what the team evaluates to be acceptable performance.

As a result, governance cannot be treated as separate from the product, even if many of its underlying decisions live in legal, compliance, security, or executive decision-making. Every distinct combination of these decisions can produce meaningfully different experiences for two people using the same model.

Consider a product that uses a model from Anthropic versus OpenAI. Each company makes different choices about model design and training, as well as safety. Those choices show up in the product as interaction patterns: what the system will answer, how cautious it feels, when it refuses, how it explains boundaries, and how much control product teams have over behavior.

Designers cannot treat these constraints as arbitrary. They shape the product and its interactions with every touchpoint. For example, a model that refuses to take certain action is an interaction, compared with a model that is eager to act.

The hardest constraints that need to be accounted for are ***rules***, which include explicit policies, laws, and restrictions that the product must respect. Rules define the boundaries of the system and shape what the product cannot do or must do, like when to disclose information or ask for permission, and where it has to stop.

Less severely enforced are ***standards***, which define optimal behavior and outcomes. These translate principles like accuracy, fairness, accessibility, safety, and more into criteria that the system can be designed and evaluated against. Customers may enforce standards contractually, but even when they are not hard rules, they provide a useful framework for tuning the model, harness, and product.

Finally, while unenforceable, ***preferences*** generate gates and incentives that shift the behavior of models and training systems over time. When Sam Altman publicly announced that GPT-4o had become "[too sycophant-y and annoying](https://x.com/sama/status/1916625892123742290)" and that the company was prioritizing adjustments, he was responding to a mismatch between the model's tuned personality and what many users wanted from it. At a smaller scale, a user's preferences for a model's voice and tone, or its saved memories and autonomy settings will affect how the system behaves within the product experience.

Designers can influence governance directly through service and policy design or direct advocacy, or indirectly by inspiring the preferences of others. Brand and communication design is a particularly effective tool for amplifying how different preferences and regulations may result in different outcomes within AI products.

At a minimum, designers need to understand the governance framework they are operating in, which may require different first-time UX, preferences, expectations, and interactions through the use of the product itself.

### Emergence

Finally, AI experiences are affected by [emergence](https://en.wikipedia.org/wiki/Emergence), the unexpected behaviors that arise when probabilistic systems operate in real-world contexts.

Plainly speaking, there is more we don't know about these models, and more we don't know that we don't know, than what we can confidently explain. Understanding their behavior is necessary to build for and with them. But we often don't know what they are capable of until we put them into play, at which point the unexpected behavior may already have played out in our customer's use of it.

Models behave differently across sessions and contexts, as well as across users, tools versions, permissions, and more. This variance can be a strength when used intentionally. In creative tools, for example, variation allows the system to generate alternative paths for exploration, or break out of an anchor that is running stale.

At the same time, variance makes AI products harder to debug. A weird generation could be the result of the model's training, its harness, outside sources or context, or simply the path the interaction took. Designers and product teams may turn to tools like evals, traces, and other observability tools to understand where the behavior drift is originating from and where the harness needs adjustment. But even then, we are not likely to fully dissect these inner workings any time soon.

This gets stranger when models develop behavior with unclear or indirect origins, like [OpenAI's "goblins" incident](https://openai.com/index/where-the-goblins-came-from/).[^2] A small personality-training incentive around common tropes related to geeky personalities eventually showed up in a broader pattern of models mentioning goblins in completely irrelevant moments.

While funny, this also revealed how small changes at the model level can cascade into visible product behavior in ways teams can't anticipate or proactively respond to. Other examples are cases where models tend to do well on complex tasks but more poorly on simpler ones, or when models seem to [glitch out](https://x.com/jameygannon/status/2061549531393646608) from random tokens.[^3]

Randomness is a necessary part of these experiences, and in fact is a feature and not a bug: uncertainty is part of what gives generative systems their value. The goal of design is not to eliminate variance or unknown behaviors, but rather to design the conditions that either minimize or mitigate these effects, and make them easier to observe, diagnose, and correct where possible.

A few first principles can guide this work. Observability helps teams see what the system is doing and how it's behaving. Interpretability helps people understand why the system appears to be following a particular path. Provenance helps teams work backward from a generation to identify how it was formed.

That makes emergence distinct from the other layers. It is not something designers configure directly. It is something they design around, monitor for, and respond to as the system encounters conditions the team could not fully predict.

## What this means for design

The expectation going forward should not be that every designer works across every layer. Full-stack AI designers need to have a general fluency across all inputs into the experience, so they can influence, mitigate, or receive the impacts that upstream work has on the end experience.

In his [2017 Design in Tech Report](https://designintech.report/wp-content/uploads/2017/03/dit-2017-1-0-7-compressed.pdf), John Maeda caught onto the trend of designers becoming more technical, but at the same time, he captured the value of traditional design. These roles are complementary, not competitive.

*John Maeda, [2017 Design in Tech Report](https://designintech.report/wp-content/uploads/2017/03/dit-2017-1-0-7-compressed.pdf)*

Technical designers are more likely to focus on the Model, Harness, and Context levels, and the role is more than just "design engineer". Other designers may focus further down the stack, as we might see design-specific titles pop up in policy making and emergent research (these roles exist today, under titles like "business designer", but have not reached critical mass within the industry). And of course, classical design will remain, but its workflows, tools, and outputs will evolve.

*In part 2 of this series, I'll explore this trend in design roles in more depth, how it relates to research around the influence of design spanning decades, and how we can prepare ourselves for the future of our work.*

⁂ Emily

*This content is 100% written by me, and [verified by Pangram](https://www.pangram.com/history/b8695b1c-5241-455d-b60b-3626235aa103). GPT 5.5 was leveraged to confirm that my definitions and descriptions were accurate to updated standards and understanding.*

---

## Footnotes

[^1]: In this way, AI design shares much in common with Systems Thinking, recognizing that the lack of direct control requires us instead to multiply our force and influence by first studying the system to determine where the leverage of our effort can be applied to the greatest effect.

[^2]: OpenAI identified that GPT-5.5 expressed an "odd affinity for goblin metaphors," seemingly a relic from the training data used to create the default "geeky" voice that users could choose from as the default persona.

[^3]: This example shows the AI app Poke sending random, unintelligible messages to a user in the flow of a conversation. Separately, Google AI results once returned 3 pages of the word "there" (and only that word) while searching for showtimes at the New York City planetarium.
