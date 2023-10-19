import re
import tiktoken
import json
import openai
import time

SRD_CC_PATH = 'utility/srd/5e-srd-cc.md'

def token_test(file_path):
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    file_string = ""
    with open(file_path, 'r') as file:
        for line in file:
            file_string += line
    return len(encoding.encode(file_string))

def read_markdown_srd(file_path):
    MARKDOWN_LINK_REGEX = r'\[([^\]]+)\]\(\#[^\)]+\)'
    MARKDOWN_SECTION_REGEX = r'\{\#[^\}]+\}$'

    lines = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                line = re.sub(MARKDOWN_LINK_REGEX, r'\1', line)
                line = re.sub(MARKDOWN_SECTION_REGEX, '', line)
                lines.append(line.strip().replace('*', ''))
    return lines

def create_entries():
    lines = read_markdown_srd(SRD_CC_PATH)
    in_list = False
    file_string = ""
    category = []

    for line in lines:
        if line[0] == '-':
            if not in_list:
                file_string = file_string[:-1]
                in_list = True
                file_string += ' [' 
            line = line[1:].strip()
            file_string += line + " / "
        elif line[0] == '<':
            pass
        else:
            if in_list:
                file_string = file_string[:-3]
                file_string += ']\n'
                in_list = False
            
            if line[0] == '#':
                hash_layer = len(line) - len(line.lstrip('#')) - 1
                while len(category) < hash_layer:
                    category.append('')
                category = category[:hash_layer]
                category.append(line.strip('#').strip())
            else:
                file_string += f"[{'/'.join(category)}] ".replace('//', '/') + line + '\n'
    return file_string.strip().split('\n')

def convert_output(output, limit = -1):
    # WARNING - COSTS MONEY
    confirmation = input("This will cost money. Are you sure you want to continue? (type 'generate embeddings' to proceed): ")
    if confirmation != "generate embeddings":
        print("Quitting out...")
        return
    version_label = input("Enter a version label for this run: ")
    openai.api_key = "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"
    to_return = []
    with open('output.txt', 'r') as file:
        line_count = len(file.readlines())
        file.seek(0)
        index = 0
        last_printed_percentage = -1
        for line in file:
            percentage = int((index / line_count) * 100)
            if percentage != last_printed_percentage:
                print(f"{percentage}% complete...")
                last_printed_percentage = percentage
            embed_entry = {"text": line}
            index += 1
            response = openai.Embedding.create(
                input=line,
                model="text-embedding-ada-002"
            )
            embed_entry["embedding"] = response['data'][0]['embedding']
            to_return.append(embed_entry)
            if limit > 0:
                limit -= 1
            if limit == 0:
                break
            time.sleep(0.02) # Delay added to prevent rate limiting
    with open(f'utility/srd/vectors/embeddings_v{version_label}.json', 'w') as file:
        print("100% complete! Writing to file...")
        json.dump(to_return, file)
    print(f"Done! Saved to embeddings_v{version_label}.json")

def main():
    entries = create_entries()
    convert_output(entries)

main()