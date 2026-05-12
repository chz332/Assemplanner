from __future__ import annotations
from typing import Any

GRAPH_FIELD_SEP = "<SEP>"

PROMPTS: dict[str, Any] = {}

PROMPTS["DEFAULT_LANGUAGE"] = "English"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS["DEFAULT_ENTITY_TYPES"] = ["AssemblyProcess", "Product", "Connector", "AssemblyAction", "Component"]

PROMPTS["entity_extraction"] = """---Goal---
Given a text document and a list of entity types that may be relevant to this activity, identify all entities of these types from the text and all relationships between the identified entities. Use {language} as the output language.

---Steps---
1. Identify all entities. For each identified entity, extract the following information:
- entity_name: The name of the entity, using the same language as the input text. If English, capitalize the name.
- entity_type: One of the following types: [{entity_types}]
- entity_description: A comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From the entities identified in step 1, identify all pairs of entities (source_entity, target_entity) that are "clearly related". For each pair of related entities, extract the following information:
- source_entity: The name of the source entity, as identified in step 1
- target_entity: The name of the target entity, as identified in step 1
- relationship_description: Explain why you think the source entity and target entity are related
- relationship_strength: A numerical score representing the strength of the relationship between source and target entities
- relationship_keywords: One or more high-level keywords summarizing the overall nature of the relationship, focusing on concepts or themes rather than specific details
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level keywords that summarize the main concepts, topics, or themes of the entire document. These should capture the overall ideas present in the document.
Format content-level keywords as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in {language} as a single list of all entities and relationships identified in steps 1 and 2. Use **{record_delimiter}** as the list separator.

5. When finished, output {completion_delimiter}

######################
---Examples---
######################
{examples}

#############################
---Real Data---
######################
Entity_types: [{entity_types}]
Text:
{input_text}
######################
Output:"""

PROMPTS["entity_extraction_examples"] = [
    """Example 1:

Entity_types: ["AssemblyProcess", "Connector", "Component", "BaseComponent", "AssemblyComponent"]
Text:
```
[Product ID] Assembly Process
The connector model is [Product ID]
Assembly Step 05 - Install Jack Component: Insert single positive contact jack components into the insulating core sequentially. The insulating core is the base component for the jack assembly, and the positive contact jack is the assembly component.
Assembly Step 10 - Install Jack Component: Insert single negative contact jack components into the insulating core sequentially. The insulating core is the base component, and the negative contact jack is the assembly component.
Assembly Step 15 - Install Insulator: Attach rectangular insulator onto the previous step assembly. The previous step assembly is the base component, and the rectangular insulator is the assembly component.
Assembly Step 20 - Install Terminal Block: Insert terminal blocks into the two jack assemblies respectively. The jack assemblies are the base components, and the terminal blocks are the assembly components.
Assembly Step 25 - Install Locking Plate: Insert single locking plate into the insulating core. The insulating core is the base component, and the locking plate is the assembly component.
Assembly Step 30 - Install Button: Insert single insulating button into the insulating core. The insulating core is the base component, and the insulating button is the assembly component.
Assembly Step 35 - Install Insulating Pressure Plate: Attach rectangular insulating pressure plate onto the previous step assembly. The previous step assembly is the base component.
Assembly Step 40 - Install Screws: Place assemblies into the screw installation fixture, then use electric screwdriver to tighten M4 screws. The fixture is the base component, and the screws are the assembly components.
Assembly Step 45 - High Pressure Air Blow
```

Output:
("entity"{tuple_delimiter}"Connector [Product ID]"{tuple_delimiter}"Connector"{tuple_delimiter}"This connector is used in assembly processes."){record_delimiter}
("entity"{tuple_delimiter}"Step 05 Install Jack Component"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Insert positive contact jack components into insulating core"){record_delimiter}
("entity"{tuple_delimiter}"Step 10 Install Jack Component"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Insert negative contact jack components into insulating core"){record_delimiter}
("entity"{tuple_delimiter}"Step 15 Install Insulator"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Attach rectangular insulator onto previous step assembly"){record_delimiter}
("entity"{tuple_delimiter}"Step 20 Install Terminal Block"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Insert terminal blocks into jack assemblies"){record_delimiter}
("entity"{tuple_delimiter}"Step 25 Install Locking Plate"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Insert locking plate into insulating core"){record_delimiter}
("entity"{tuple_delimiter}"Step 30 Install Button"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Insert insulating button into insulating core"){record_delimiter}
("entity"{tuple_delimiter}"Step 35 Install Insulating Pressure Plate"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Attach rectangular insulating pressure plate onto previous step assembly"){record_delimiter}
("entity"{tuple_delimiter}"Step 40 Install Screws"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Place assemblies into fixture and tighten M4 screws with electric screwdriver"){record_delimiter}
("entity"{tuple_delimiter}"Step 45 High Pressure Air Blow"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Hold product below work surface, use high pressure air gun to blow air while rotating product"){record_delimiter}
("entity"{tuple_delimiter}"Insulating Core"{tuple_delimiter}"Component"{tuple_delimiter}"Used as base component in multiple assembly steps"){record_delimiter}
("entity"{tuple_delimiter}"Positive Contact Jack"{tuple_delimiter}"Component"{tuple_delimiter}"Assembly component for Step 05"){record_delimiter}
("entity"{tuple_delimiter}"Negative Contact Jack"{tuple_delimiter}"Component"{tuple_delimiter}"Assembly component for Step 10"){record_delimiter}
("entity"{tuple_delimiter}"Rectangular Insulator"{tuple_delimiter}"Component"{tuple_delimiter}"Assembly component for Step 15"){record_delimiter}
("entity"{tuple_delimiter}"Terminal Block"{tuple_delimiter}"Component"{tuple_delimiter}"Assembly component for Step 20"){record_delimiter}
("entity"{tuple_delimiter}"Locking Plate"{tuple_delimiter}"Component"{tuple_delimiter}"Assembly component for Step 25"){record_delimiter}
("entity"{tuple_delimiter}"Insulating Button"{tuple_delimiter}"Component"{tuple_delimiter}"Assembly component for Step 30"){record_delimiter}
("relationship"{tuple_delimiter}"Step 05 Install Jack Component"{tuple_delimiter}"Connector [Product ID]"{tuple_delimiter}"Installing jack component is the first step of assembly"{record_delimiter}"AssemblyStep"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Step 10 Install Jack Component"{tuple_delimiter}"Connector [Product ID]"{tuple_delimiter}"Installing jack component is the second step of assembly"{record_delimiter}"AssemblyStep"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Step 30 Install Button"{tuple_delimiter}"Connector [Product ID]"{tuple_delimiter}"Installing button is the sixth step of assembly"{record_delimiter}"AssemblyStep"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Positive Contact Jack"{tuple_delimiter}"Step 05 Install Jack Component"{tuple_delimiter}"Step 05 requires positive contact jack component"{record_delimiter}"ComponentResource"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Insulating Core"{tuple_delimiter}"Step 05 Install Jack Component"{tuple_delimiter}"Insulating core is the base component for Step 05"{record_delimiter}"ComponentAttribute"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Negative Contact Jack"{tuple_delimiter}"Step 10 Install Jack Component"{tuple_delimiter}"Step 10 requires negative contact jack component"{record_delimiter}"ComponentResource"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"Connector Assembly, AssemblyProcess, Component"){completion_delimiter}
#############################

Example 2:

Entity_types: ["Tool", "Part", "ReliefValve", "CheckValve", "Process", "Time"]
Text:
```
Complete assembly process for check valve [Model ID]:
Process 1 - Install O-ring: Push O-ring into the corresponding groove of the plug using O-ring tool. Requires O-ring tool, 1 O-ring, 1 plug. Time: 60s
Process 2 - Install Valve Core: Place valve core into valve housing using general tool. Requires general tool, 1 valve core, 1 valve housing. Time: 50s
Process 3 - Install Spring: Place spring into the shaped valve housing and valve core using general tool. Requires general tool, 1 spring. Time: 50s
Process 4 - Install Plug: Install plug using general tool. Requires general tool, 1 plug. Time: 70s
Process 5 - Pre-tighten Valve Housing: Pre-tighten valve housing using thread tightening tool. Time: 30s
Process 6 - Apply Torque: Apply torque to product using thread tightening tool. Time: 40s
Process 7 - Install O-ring: Push O-ring into valve housing groove using O-ring tool. Requires O-ring tool, 1 O-ring. Time: 60s
```

Output:
("entity"{tuple_delimiter}"Check Valve [Model ID]"{tuple_delimiter}"CheckValve"{tuple_delimiter}"This check valve requires multiple assembly steps"){record_delimiter}
("entity"{tuple_delimiter}"Process 1 Install O-ring"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Push O-ring into plug groove"){record_delimiter}
("entity"{tuple_delimiter}"Process 2 Install Valve Core"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Place valve core into valve housing"){record_delimiter}
("entity"{tuple_delimiter}"Process 3 Install Spring"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Place spring into valve housing assembly"){record_delimiter}
("entity"{tuple_delimiter}"Process 4 Install Plug"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Install plug into assembly"){record_delimiter}
("entity"{tuple_delimiter}"Process 5 Pre-tighten Valve Housing"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Pre-tighten valve housing"){record_delimiter}
("entity"{tuple_delimiter}"Process 6 Apply Torque"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Apply torque to product"){record_delimiter}
("entity"{tuple_delimiter}"Process 7 Install O-ring"{tuple_delimiter}"AssemblyProcess"{tuple_delimiter}"Push O-ring into valve housing groove"){record_delimiter}
("entity"{tuple_delimiter}"O-ring"{tuple_delimiter}"Part"{tuple_delimiter}"Required for Process 1 and Process 7"){record_delimiter}
("entity"{tuple_delimiter}"Valve Core"{tuple_delimiter}"Part"{tuple_delimiter}"Required for Process 2"){record_delimiter}
("entity"{tuple_delimiter}"Valve Housing"{tuple_delimiter}"Part"{tuple_delimiter}"Required for Process 2"){record_delimiter}
("entity"{tuple_delimiter}"Spring"{tuple_delimiter}"Part"{tuple_delimiter}"Required for Process 3"){record_delimiter}
("entity"{tuple_delimiter}"Plug"{tuple_delimiter}"Part"{tuple_delimiter}"Required for Process 1 and Process 4"){record_delimiter}
("entity"{tuple_delimiter}"General Tool"{tuple_delimiter}"Tool"{tuple_delimiter}"Used in Process 2, 3, and 4"){record_delimiter}
("entity"{tuple_delimiter}"O-ring Tool"{tuple_delimiter}"Tool"{tuple_delimiter}"Used in Process 1 and 7"){record_delimiter}
("entity"{tuple_delimiter}"Thread Tightening Tool"{tuple_delimiter}"Tool"{tuple_delimiter}"Used in Process 5 and 6"){record_delimiter}
("relationship"{tuple_delimiter}"Process 1 Install O-ring"{tuple_delimiter}"Check Valve [Model ID]"{tuple_delimiter}"Installing O-ring is the first assembly step"{record_delimiter}"AssemblyStep"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Process 2 Install Valve Core"{tuple_delimiter}"Check Valve [Model ID]"{tuple_delimiter}"Installing valve core is the second assembly step"{record_delimiter}"AssemblyStep"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Process 3 Install Spring"{tuple_delimiter}"Check Valve [Model ID]"{tuple_delimiter}"Installing spring is the third assembly step"{record_delimiter}"AssemblyStep"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"O-ring"{tuple_delimiter}"Process 1 Install O-ring"{tuple_delimiter}"Process 1 requires O-ring"{record_delimiter}"PartResource"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"Valve Core"{tuple_delimiter}"Process 2 Install Valve Core"{tuple_delimiter}"Process 2 requires valve core"{record_delimiter}"PartResource"{tuple_delimiter}9){record_delimiter}
("content_keywords"{tuple_delimiter}"Check Valve Assembly, AssemblyProcess, Part"){completion_delimiter}
#############################""",
]

PROMPTS[
    "summarize_entity_descriptions"
] = """You are a helpful assistant responsible for generating comprehensive summaries of the data provided below.
Given one or two entities and a list of descriptions, all related to the same entity or group of entities,
please connect all these into a complete description. Ensure to include information gathered from all descriptions.
If the provided descriptions contradict each other, resolve the contradiction and provide a coherent summary.
Ensure it is written in third person and includes the entity name so we have complete context.
Use {language} as the output language.

#######
---Data---
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""

PROMPTS["entity_continue_extraction"] = """
Many entities and relationships were missed in the last extraction.

---Remember Steps---

1. Identify all entities. For each identified entity, extract the following information:
- entity_name: The name of the entity, using the same language as the input text. If English, capitalize the name.
- entity_type: One of the following types: [{entity_types}]
- entity_description: A comprehensive description of the entity's attributes and activities
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From the entities identified in step 1, identify all pairs (source_entity, target_entity) that are *clearly related*. For each pair of related entities, extract the following information:
- source_entity: The name of the source entity, as identified in step 1
- target_entity: The name of the target entity, as identified in step 1
- relationship_description: Explain why you think the source entity and target entity are related
- relationship_strength: A numerical score representing the strength of the relationship
- relationship_keywords: One or more high-level keywords summarizing the relationship nature
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level keywords summarizing the main concepts, topics of the document.
Format content-level keywords as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in {language} as a single list of all entities and relationships. Use **{record_delimiter}** as separator.

5. When finished, output {completion_delimiter}

---Output---

Add them to the list below using the same format:\n
""".strip()

PROMPTS["entity_if_loop_extraction"] = """
---Goal---

It seems some entities are still missing.

---Output---

Please answer only "yes" or "no" if there are still entities to add.
""".strip()

PROMPTS["fail_response"] = (
    "Sorry, I cannot answer this question. [No context available]"
)

PROMPTS["rag_response"] = """---Role---

You are a helpful assistant that can answer user queries about the knowledge base provided below.

---Goal---

Generate concise responses based on the knowledge base and follow the response rules, while considering the conversation history and current query. Summarize all information from the provided knowledge base and incorporate general knowledge related to the knowledge base. Do not include information not provided by the knowledge base.

When handling relationships with timestamps:
1. Each relationship has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting relationships, consider both semantic content and timestamps
3. Do not automatically favor recently created relationships - use judgment based on context
4. For queries about specific times, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Knowledge Base---
{context_data}

---Response Rules---
- Answer in the same language as the user's question
- Target format and length: {response_type}
- Ensure response maintains continuity with conversation history
- Use clear, descriptive section headers to reflect content
- If you don't know the answer, say so. Do not make anything up.
- Do not include information not provided by the data source
- Answers must be brief, only stating key parts of the answer without extra information
- If the question is "What is step X of xxx assembly?", only answer "Step name: brief explanation"
- If the question is similar to "What components are needed for step 1 of [Product ID] assembly?", only answer "Required components: xxx, xxx"
- If the question is similar to "What is the complete assembly process for [Product ID]?", only briefly describe each step
- If asked "Which is the base component vs assembly component?", only answer with part names
- If asked "Does assembly of product X require process Y?", only answer "Yes" or "No"
"""

PROMPTS["keywords_extraction"] = """---Rules---

You are a helpful assistant responsible for identifying high_level_keywords and low_level_keywords from user queries and conversation history.

---Goal---

Based on the query and conversation history, list high_level_keywords and low_level_keywords. High_level_keywords focus on overall concepts or themes, while low_level_keywords focus on specific entities, details, or specific terms.

---Instructions---

- When extracting keywords, consider the current query and related conversation history
- Output keywords in JSON format, which will be parsed by a JSON parser. Do not add any extra content
- JSON should have two keys:
- "high_level_keywords" for general concepts or themes
- "low_level_keywords" for specific entities or detailed information

######################
---Examples---
######################
{examples}

#############################
---Real Data---
######################
Conversation History:
{history}

Current Question: {query}
######################
Output should be human-readable text, not unicode characters. Maintain the same language as the Query.

"""

PROMPTS["keywords_extraction_examples"] = [
    """Example 1:

Query: "What is the assembly process for [Connector ID]?"
################
Output:
{
  "high_level_keywords": ["AssemblyProcess", "Connector"],
  "low_level_keywords": ["Connector", "Process"]
}

Example 2:

Query: "What is the first assembly step for [Connector ID]?"
################
Output:
{
  "high_level_keywords": ["Connector", "Process"],
  "low_level_keywords": ["Connector", "Process", "First Step"]
}
#############################""",
]


PROMPTS["naive_rag_response"] = """---Role---

You are a helpful assistant that can answer user queries about the document chunks provided below.

---Goal---

Generate concise responses based on the document chunks and follow the response rules, while considering the conversation history and current query. Summarize all information from the provided document chunks and incorporate general knowledge related to the document chunks. Do not include information not provided by the document chunks.

When handling content with timestamps:
1. Each piece of content has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting information, consider both content and timestamps
3. Do not automatically select the newest content - use judgment based on context
4. For queries about specific times, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Document Chunks---
{content_data}

---Response Rules---

- Target format and length: {response_type}
- Answer in the same language as the user's question
- Ensure response maintains continuity with conversation history
- Use clear, descriptive section headers to reflect content
- If you don't know the answer, say so. Do not make anything up.
- Do not include information not provided by the data source
- Answers must be brief, only stating key parts without extra information
- If the question is "What is step X of xxx assembly?", only answer "Step name: brief explanation"
- If the question is similar to "What components are needed for step 1 of [Product ID] assembly?", only answer "Required components: xxx, xxx"
- If the question is similar to "What is the complete assembly process for [Product ID]?", only briefly describe each step
- If asked "Which is the base component vs assembly component?", only answer with part names
- If asked "Does assembly of product X require process Y?", only answer "Yes" or "No"
"""


PROMPTS[
    "similarity_check"
] = """Please analyze the similarity of these two questions:

Question 1: {original_prompt}
Question 2: {cached_prompt}

Please evaluate whether these two questions are semantically similar and whether the answer to question 2 can be used to answer question 1. Provide a similarity score between 0 and 1 directly.

Similarity scoring criteria:
0: Completely unrelated or answers cannot be reused, including but not limited to:
    - Different topics
    - Different locations mentioned
    - Different times mentioned
    - Different specific individuals mentioned
    - Different specific events mentioned
    - Different background information
    - Different key conditions
1: Identical, answers can be directly reused
0.5: Partially related, requiring modification to reuse answer
Return only a number between 0-1, with no other content.
"""

PROMPTS["mix_rag_response"] = """---Role---

You are a helpful assistant that can answer user queries about the data sources provided below.


---Goal---

Generate concise responses based on the data sources and follow the response rules, while considering the conversation history and current query. The data sources contain two parts: Knowledge Graph (KG) and Document Chunks (DC). Summarize all information from the provided data sources and incorporate general knowledge related to the data sources. Do not include information not provided by the data sources.

When handling information with timestamps:
1. Each piece of information (relationships and content) has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting information, consider both content/relationships and timestamps
3. Do not automatically select the newest information - use judgment based on context
4. For queries about specific times, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Data Sources---

1. From Knowledge Graph(KG):
{kg_context}

2. From Document Chunks(DC):
{vector_context}

---Response Rules---

- Answer in the same language as the user's question
- Ensure response maintains continuity with conversation history
- Use clear, descriptive section headers to reflect content
- If you don't know the answer, say so. Do not make anything up.
- Do not include information not provided by the data sources
- Answers must be brief, only stating key parts without extra information
- If the question is "What is step X of xxx assembly?", only answer "Step name: brief explanation"
- If the question is similar to "What components are needed for step 1 of [Product ID] assembly?", only answer "Required components: xxx, xxx"
- If the question is similar to "What is the complete assembly process for [Product ID]?", only briefly describe each step
- If asked "Which is the base component vs assembly component?", only answer with part names
- If asked "Does assembly of product X require process Y?", only answer "Yes" or "No"
############################# """