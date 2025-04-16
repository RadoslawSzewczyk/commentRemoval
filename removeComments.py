import os
import sys

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
        blockStartIdx = line.find('/*')
        if blockStartIdx != -1 and (lineCommentIdx == -1 or blockStartIdx < lineCommentIdx):
            endIdx = line.find('*/', blockStartIdx+2)
            if endIdx == -1:
                return line[:blockStartIdx], True
            else:
                newLine = line[:blockStartIdx] + line[endIdx+2:]
                return processCstyleLine(newLine, False)
        elif lineCommentIdx != -1:
            return line[:lineCommentIdx], False
        else:
            return line, False

def processHtmlLine(line, inComment):
    if inComment:
        endIdx = line.find('-->')
        if endIdx == -1:
            return '', True
        else:
            line = line[endIdx+3:]
            inComment = False
            return processHtmlLine(line, inComment)[0], inComment
    else:
        startIdx = line.find('<!--')
        if startIdx == -1:
            return line, False
        else:
            endIdx = line.find('-->', startIdx+4)
            if endIdx == -1:
                return line[:startIdx], True
            else:
                newLine = line[:startIdx] + line[endIdx+3:]
                return processHtmlLine(newLine, False)[0], False

def processHashLine(line):
    return line.split('#')[0].rstrip() + '\n'

def processSemicolonLine(line):
    return line.split(';')[0].rstrip() + '\n'

def processPercentLine(line):
    return line.split('%')[0].rstrip() + '\n'

def processDashLine(line, comment_marker="--"):
    return line.split(comment_marker)[0].rstrip() + '\n'

def processHaskellLine(line, inBlock):
    if inBlock:
        endIdx = line.find('-}')
        if endIdx == -1:
            return '', True
        else:
            inBlock = False
            return line[endIdx+2:], inBlock
    else:
        lineCommentIdx = line.find('--')
        blockStartIdx = line.find('{-')
        if blockStartIdx != -1 and (lineCommentIdx == -1 or blockStartIdx < lineCommentIdx):
            endIdx = line.find('-}', blockStartIdx+2)
            if endIdx == -1:
                return line[:blockStartIdx], True
            else:
                newLine = line[:blockStartIdx] + line[endIdx+2:]
                return processHaskellLine(newLine, False)
        elif lineCommentIdx != -1:
            return line[:lineCommentIdx], False
        else:
            return line, False

def processLuaLine(line, inBlock):
    if inBlock:
        endIdx = line.find("]]")
        if endIdx != -1:
            inBlock = False
            remainder = line[endIdx+2:]
            return processLuaLine(remainder, inBlock)
        else:
            return "", True
    else:
        startIdx = line.find("--[[")
        if startIdx != -1:
            # Keep any code before the block comment.
            codeBefore = line[:startIdx]
            # Look for the closing marker on the same line.
            remainder = line[startIdx+4:]
            endIdx = remainder.find("]]")
            if endIdx != -1:
                inBlock = False
                # Remove comment block on this line and process any remaining text.
                new_line = codeBefore + remainder[endIdx+2:]
                return processLuaLine(new_line, inBlock)
            else:
                # Block comment starts and continues on following lines.
                return codeBefore, True
        else:
            # Process single-line Lua comments (starting with --)
            singleIdx = line.find("--")
            if singleIdx != -1:
                return line[:singleIdx], False
            else:
                return line, False

def processDelphiLine(line, state):
    if state.get("inBlock", False):
        end_marker = state["block_end"]
        endIdx = line.find(end_marker)
        if endIdx == -1:
            return '', state
        else:
            state["inBlock"] = False
            state["block_end"] = None
            return line[endIdx+len(end_marker):], state
    lineCommentIdx = line.find('//')
    block1Idx = line.find('{')
    block2Idx = line.find('(*')
    blockStartIdx = -1
    block_marker = None
    if block1Idx != -1:
        blockStartIdx = block1Idx
        block_marker = "}"
    if block2Idx != -1 and (blockStartIdx == -1 or block2Idx < blockStartIdx):
        blockStartIdx = block2Idx
        block_marker = "*)"
    if blockStartIdx != -1 and (lineCommentIdx == -1 or blockStartIdx < lineCommentIdx):
        endIdx = line.find(block_marker, blockStartIdx + (1 if block_marker == "}" else 2))
        if endIdx == -1:
            state["inBlock"] = True
            state["block_end"] = block_marker
            return line[:blockStartIdx], state
        else:
            newLine = line[:blockStartIdx] + line[endIdx+len(block_marker):]
            return processDelphiLine(newLine, state)
    elif lineCommentIdx != -1:
        return line[:lineCommentIdx], state
    else:
        return line, state

def processCobolLine(line):
    if len(line) >= 7 and line[6] == '*':
        return ''
    else:
        return line

def processSASLine(line, inBlock):
    stripped = line.strip()
    if stripped.startswith('*') and stripped.endswith(';'):
        return '', inBlock
    return processCstyleLine(line, inBlock)

def processVBNetLine(line):
    return line.split("'")[0].rstrip() + '\n'

def processABAPLine(line):
    stripped = line.lstrip()
    if stripped.startswith('*') or stripped.startswith('"'):
        return ''
    else:
        return line

def processPythonLine(line, inTriple):
    if inTriple:
        endIdx = line.find('"""')
        if endIdx == -1:
            return '', True
        else:
            line = line[endIdx+3:]
            inTriple = False
            return line.split('#')[0].rstrip() + '\n', inTriple
    else:
        tripleStart = line.find('"""')
        hashIndex = line.find('#')
        if tripleStart != -1 and (hashIndex == -1 or tripleStart < hashIndex):
            endIdx = line.find('"""', tripleStart+3)
            if endIdx == -1:
                return line[:tripleStart], True
            else:
                newLine = line[:tripleStart] + line[endIdx+3:]
                return newLine.split('#')[0].rstrip() + '\n', False
        elif hashIndex != -1:
            return line.split('#')[0].rstrip() + '\n', False
        else:
            return line, False

def removeCommentsGenerator(lines, language):
    if language == "c-style":
        inBlock = False
        for line in lines:
            line, inBlock = processCstyleLine(line, inBlock)
            if line.strip():
                yield line
    elif language == "html":
        inComment = False
        for line in lines:
            line, inComment = processHtmlLine(line, inComment)
            if line.strip():
                yield line
    elif language == "python":
        inTriple = False
        for line in lines:
            line, inTriple = processPythonLine(line, inTriple)
            if line.strip():
                yield line
    elif language == "r":
        for line in lines:
            line = processHashLine(line)
            if line.strip():
                yield line
    elif language == "hash-style":
        for line in lines:
            line = processHashLine(line)
            if line.strip():
                yield line
    elif language == "semicolon-style":
        for line in lines:
            line = processSemicolonLine(line)
            if line.strip():
                yield line
    elif language == "percent-style":
        for line in lines:
            line = processPercentLine(line)
            if line.strip():
                yield line
    elif language == "ada":
        for line in lines:
            line = processDashLine(line, comment_marker="--")
            if line.strip():
                yield line
    elif language == "haskell":
        inBlock = False
        for line in lines:
            line, inBlock = processHaskellLine(line, inBlock)
            if line.strip():
                yield line
    elif language == "lua":
        inBlock = False
        for line in lines:
            line, inBlock = processLuaLine(line, inBlock)
            if line.strip():
                yield line
    elif language == "delphi":
        state = {"inBlock": False, "block_end": None}
        for line in lines:
            line, state = processDelphiLine(line, state)
            if line.strip():
                yield line
    elif language == "cobol":
        for line in lines:
            line = processCobolLine(line)
            if line.strip():
                yield line
    elif language == "sas":
        inBlock = False
        for line in lines:
            line, inBlock = processSASLine(line, inBlock)
            if line.strip():
                yield line
    elif language == "vbnet":
        for line in lines:
            line = processVBNetLine(line)
            if line.strip():
                yield line
    elif language == "abap":
        for line in lines:
            line = processABAPLine(line)
            if line.strip():
                yield line
    else:
        for line in lines:
            if line.strip():
                yield line

def main():
    supportedLanguages = [
        "c-style",
        "html",
        "python",
        "r",
        "hash-style",
        "semicolon-style",
        "percent-style",
        "ada",
        "haskell",
        "lua",
        "delphi",
        "cobol",
        "sas",
        "vbnet",
        "abap"
    ]
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
            choice = int(input("Choose language (number): "))
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
        with open(file_path, 'r', encoding='utf-8') as infile, open(newFilePath, 'w', encoding='utf-8') as outfile:
            cleaned_lines = removeCommentsGenerator(infile, language)
            for line in cleaned_lines:
                outfile.write(line)
        print(f"Comments removed. Clean file saved as: {newFilePath}")
    except Exception as e:
        print(f"Error processing file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
