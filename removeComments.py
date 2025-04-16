import os
import sys

def removeCommentsGenerator(lines, language):
    inBlockComment = False
    for line in lines:
        if language in ["c style (go, js, php, cpp)"]:
            line, inBlockComment = processCstyleLine(line, inBlockComment)
        elif language == "html":
            line = processHtmlLine(line)
        elif language in ["python, r"]:
            line = process_python_r_line(line)
        yield line

def processCstyleLine(line, inBlock):
    if inBlock:
        endIdx = line.find('*/')
        if endIdx == -1:
            return '', True
        else:
            inBlock = False
            return line[endIdx+2:], inBlock
    else:
        lineCommentIdx = line.find('//')
        block_startIdx = line.find('/*')
        if block_startIdx != -1 and (lineCommentIdx == -1 or block_startIdx < lineCommentIdx):
            endIdx = line.find('*/', block_startIdx+2)
            if endIdx == -1:
                return line[:block_startIdx], True
            else:
                newLine = line[:block_startIdx] + line[endIdx+2:]
                return processCstyleLine(newLine, False)
        elif lineCommentIdx != -1:
            return line[:lineCommentIdx], False
        else:
            return line, False

def processHtmlLine(line):
    while True:
        startIdx = line.find('<!--')
        if startIdx == -1:
            break
        endIdx = line.find('-->', startIdx+4)
        if endIdx == -1:
            line = line[:startIdx]
            break
        line = line[:startIdx] + line[endIdx+3:]
    return line

def process_python_r_line(line):
    return line.split('#')[0].rstrip() + '\n'

def main():
    supportedLanguages = ["go, js, php, cpp", "html", "python, r"]

    file_path = input("Enter the path to the code file: ").strip()
    if not os.path.isfile(file_path):
        print("Error: The file does not exist.")
        sys.exit(1)

    print("Select a programming language for comment removal:")
    for idx, lang in enumerate(supportedLanguages, 1):
        print(f"{idx}. {lang}")
    
    language = None
    while not language:
        try:
            choice = int(input("Choose language: "))
            if 1 <= choice <= len(supportedLanguages):
                language = supportedLanguages[choice - 1]
            else:
                print(f"Please enter a number between 1 and {len(supportedLanguages)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    print(f"You selected: {language}")

    base, ext = os.path.splitext(file_path)
    newFilePath = f"{base}_nocomments{ext}"

    try:
        with open(file_path, 'r', encoding='utf-8') as infile, \
             open(newFilePath, 'w', encoding='utf-8') as outfile:

            cleaned_lines = removeCommentsGenerator(infile, language)
            for line in cleaned_lines:
                outfile.write(line)

        print(f"Comments removed. Clean file saved as: {newFilePath}")
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()