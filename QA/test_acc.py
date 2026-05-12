from openai import OpenAI
import json
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client._client.api_base = os.getenv("OPENAI_API_BASE")


def read_json_qa_pairs(file_path):
    """Read QA pairs from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                pairs = [(item["question"], item["answer"]) for item in data if "question" in item and "answer" in item]
                print(f"Successfully read {file_path}, {len(pairs)} QA pairs")
                return pairs
            else:
                print(f"{file_path} content is not a list, actual type: {type(data)}")
                return []
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {file_path}: {e}")
        return []


def compare_and_output_each_pair(generated_pairs, reference_pairs, output_file):
    """Compare generated answers with reference answers"""
    total = min(len(generated_pairs), len(reference_pairs))
    if total == 0:
        print("No data to compare, please check input files.")
        return

    if os.path.exists(output_file):
        os.remove(output_file)

    correct_count = 0
    for i in range(total):
        gen_q, gen_a = generated_pairs[i]
        ref_q, ref_a = reference_pairs[i]

        messages = [
            {"role": "system", "content": "You are a judge"},
            {"role": "user", "content":
                f"""Evaluate if the generated question and answer are correct:
Question: {gen_q}
Answer: {gen_a}

Reference Question: {ref_q}
Reference Answer: {ref_a}

Please determine if the generated question and answer are "correct". Output only "correct" or "wrong". If the answer doesn't address the question, output "question_not_matched". Just output the result without explanation."""}
        ]

        try:
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=messages,
                temperature=0.9,
                max_tokens=100,
                top_p=1,
                n=1,
            )
            judgment = response.choices[0].message.content.strip()

            if judgment == "correct":
                correct_count += 1

            with open(output_file, "a", encoding="utf-8") as f:
                f.write(
                    f"QA Pair {i+1} comparison result:\n"
                    f"[Generated Question] {gen_q}\n"
                    f"[Generated Answer] {gen_a}\n"
                    f"[Reference Question] {ref_q}\n"
                    f"[Reference Answer] {ref_a}\n"
                    f"[Judgment] {judgment}\n\n"
                )

            print(f"QA Pair {i+1} comparison completed: {judgment}")

        except Exception as e:
            error_msg = f"Error comparing QA Pair {i+1}: {e}"
            print(error_msg)
            with open(output_file, "a", encoding="utf-8") as f:
                f.write(error_msg + "\n")

    accuracy = (correct_count / total) * 100
    summary = f"\nTotal compared: {total} pairs\nCorrect: {correct_count} pairs\nAccuracy: {accuracy:.2f}%\n"
    print(summary)
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(summary)


if __name__ == "__main__":
    generated_file = "QA/answer.json"
    reference_file = "QA/questions&reference/reference_5.json"
    output_file = "QA/comparison_results5_withoutrag.txt"

    generated_pairs = read_json_qa_pairs(generated_file)
    reference_pairs = read_json_qa_pairs(reference_file)

    if generated_pairs and reference_pairs:
        compare_and_output_each_pair(generated_pairs, reference_pairs, output_file)

    print("done ✅")