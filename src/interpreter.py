"""
Contains routines for parsing and executing the game's custom language.
"""

from global_vars import Globals

class BodyNode:
    """ Node containing a mixture of natural language and functions as child nodes """

    def __init__(self, nodes=[]):
        """ contains a sequence of LangNodes and FuncNodes """
        self.nodes = nodes

    def __str__(self):
        ret = "BodyNode[\n"
        for a in self.nodes:
            ret += str(a)
        ret += "]\n"
        return ret

class LangNode:
    """ Node that contains natural language to be displayed in game """

    def __init__(self, text='', formatting={}):
        """ text to be displayed in game """
        self.text = text
        # remove beginning forward slash (syntax for preserving leading spaces)
        lines = self.text.split('\n')
        lines = [(line[1:] if len(line) > 0 and line[0] == '\\' else line) for line in lines]
        self.text = '\n'.join(lines)

        """ formatting for text to modify color or style """
        self.formatting = formatting

    def __str__(self):
        ret = "LangNode(text: " + self.text.replace("\n"," \\n ") + ", formatting: {"
        for c in self.formatting.keys():
            ret += c + ": " + str(self.formatting[c]) + ", "
        ret += "})\n"
        return ret

class FuncNode:
    """ Node that contains a function to be evaluated during runtime """

    def __init__(self, title='', args=[], inner=None):
        """ a string of the function name """
        self.title = title
        """ a list of strings of function parameters (other tokens separated by underscores) """
        self.args = args
        """
        type of self.inner depends on self.title:
            if, elif, else -> BodyNode - gets executed if condition in args is true
            choice -> (LangNode, BodyNode)[] - the BodyNode result for the chosen LangNode option is executed
            random -> BodyNode[] - one from list gets randomly executed
        for other functions without {}, self.inner is None
        """
        self.inner = inner

    def __str__(self):
        ret = "FuncNode(title: " + self.title + ", args: " + str(self.args)
        if self.inner is not None:
            ret += ", inner: [\n"
            if self.title == 'if' or self.title == 'elif' or self.title == 'else':
                ret += str(self.inner)
            elif self.title == 'choice':
                for a in self.inner:
                    ret += "("
                    ret += "choice: " + str(a[0])
                    ret += "result: " + str(a[1])[:-1]
                    ret += "),\n"
            elif self.title == 'random':
                for a in self.inner:
                    ret += str(a)
            ret += "])\n"
        else:
            ret += ")\n"
        return ret

class Interpreter:
    """ Contains parsing and execution routines for the game's custom scripting language. """

    def __init__(self):
        pass

    def matchingBraceIndex(self, string, startInd=0):
        """ identify index of matching close brace """
        nextInd = startInd
        openCount = 1
        while True:
            openInd = string.find('{', nextInd)
            closeInd = string.find('}', nextInd)
            if closeInd == -1:
                raise Exception('No matching brace in string:\n' + string)
            elif openInd != -1 and openInd < closeInd:
                openCount += 1
                nextInd = openInd + 1
            else:
                openCount -= 1
                if openCount == 0:
                    return closeInd
                nextInd = closeInd + 1

    def splitByPipe(self, string, startInd=0):
        """ performs a split by vertical pipe, accounting for functions """
        # remainingInd represents where unprocessed string starts
        remainingInd = startInd
        # seekInd indicates where to start looking for a pipe
        seekInd = startInd
        # results contains the split substrings
        results = []
        while remainingInd < len(string):
            # find the pipe
            pipeInd = string.find('|', seekInd)
            # no more pipes -> done
            if pipeInd == -1:
                break
            # find the opening of a function
            openInd = string.find('{', seekInd)
            # if function opens before pipe, the pipe might be part of subfunction inner
            if openInd != -1 and openInd < pipeInd:
                # skip past the function and retry
                closeInd = self.matchingBraceIndex(string, openInd+1)
                seekInd = closeInd + 1
            # otherwise the pipe is part of this function inner
            else:
                # capture the substring and continue
                results.append(string[remainingInd:pipeInd])
                seekInd = pipeInd + 1
                remainingInd = pipeInd + 1
        # append element between last pipe and end of string
        if remainingInd < len(string):
            results.append(string[remainingInd:])
        return results

    def parseFormat(self, text):
        """
        Reads color/style formatted text and returns
        LangNode(text, {formatter1 : [(index1,index2), (index3, index4)], formatter2 : ...})
        """
        #index_of_at will track the last instance of the "@" character in the text
        index_of_at = 0
        index_close_bracket = -1
        previous_close_bracket = -1
        index_open_bracket = -1
        formatting = {} # dictionary of formation {string : tuple} of formatters and where they apply
        text_without_formatters = ""

        #While there are remaining "@"s in the string, format into a LangNode
        while text.find("@", index_of_at) != -1:
            index_of_at = text.find("@", index_of_at)
            index_open_bracket = text.find("{", index_of_at)
            index_close_bracket = text.find("}", index_of_at)

            #if no close or open bracket exists, exit the method and return error message
            if index_open_bracket == -1:
                raise Exception("The formatter is missing an opening bracket: \n" + text)
            if index_close_bracket == -1:
                raise Exception("The formatter is missing an closing bracket: \n" + text)

            # the formatted text looks like @formatter{formatted_text}
            formatter = text[index_of_at + 1 : index_open_bracket].strip()
            formatted_text = text[index_open_bracket + 1 : index_close_bracket]

            # text_without_formatters will hold the text with the @formatter{formattted_text} replaced with just formatted_text
            text_without_formatters += text[previous_close_bracket + 1 : index_of_at]
            text_without_formatters += formatted_text

            if Globals.IsDev:
                print("index_of_at: " + str(index_of_at))
                print("index_open_bracket: " + str(index_open_bracket))
                print("index_close_bracket: " + str(index_close_bracket))
                print("formatter: " + formatter)
                print("formatted_text: " + formatted_text + "\n")

            # Remember where in the text_without_formatters string each formatter applies
            if formatter not in formatting:
                formatting[formatter] = []
            formatting[formatter].append((len(text_without_formatters)-len(formatted_text), len(text_without_formatters) -1))

            previous_close_bracket = index_close_bracket # remember where the previous } was
            index_of_at = index_of_at + 1   # start searching for the next @ after the previous @

        # capture remaining unformatted text
        text_without_formatters += text[previous_close_bracket+1:]
        return LangNode(text_without_formatters, formatting)

    def parseBody(self, scriptStr):
        """ Converts a string into a BodyNode """
        remainingInd = 0
        nodes = []
        while remainingInd < len(scriptStr):
            # locate a function by searching for $
            funcInd = scriptStr.find('$', remainingInd)
            # function not found -> all content can be captured in LangNode
            functionExists = funcInd != -1
            # if content exists between current index and function, store in LangNode
            if not functionExists:
                langStr = scriptStr[remainingInd:].strip()
            else:
                langStr = scriptStr[remainingInd:funcInd].strip()
            if langStr != "":
                langNode = self.parseFormat(langStr)
                nodes.append(langNode)
            # only proceed with function parsing if function exists
            if not functionExists:
                break
            # determine if function has inner (part surrounded by {})
            braceOpenInd = scriptStr.find('{', funcInd)
            innerExists = (braceOpenInd != -1 and len(scriptStr[funcInd:braceOpenInd].split()) == 1)
            # index where function name ends
            funcNameEndInd = 0
            # string containing function inner, if it exists
            funcInnerStr = None
            # function has inner -> parse that portion
            if innerExists:
                braceCloseInd = self.matchingBraceIndex(scriptStr, braceOpenInd + 1)
                funcInnerStr = scriptStr[braceOpenInd+1:braceCloseInd]
                funcNameEndInd = braceOpenInd
                remainingInd = braceCloseInd + 1
            # function has no inner
            else:
                # function description ends on newline
                newlineInd = scriptStr.find('\n', funcInd)
                if newlineInd == -1:
                    newlineInd = len(scriptStr) - 1
                funcNameEndInd = newlineInd
                remainingInd = newlineInd + 1
            # parse function title and args
            funcAllArgs = scriptStr[funcInd+1:funcNameEndInd].strip().split('_')
            funcTitle = funcAllArgs[0]
            funcArgs = funcAllArgs[1:]
            funcInner = None
            # parse inner based on title
            if funcTitle == 'if' or funcTitle == 'elif' or funcTitle == 'else':
                funcInner = self.parseBody(funcInnerStr.strip())
            elif funcTitle == 'choice':
                choices = self.splitByPipe(funcInnerStr.strip())
                funcInner = []
                option = None
                result = None
                for i in range(len(choices)):
                    if i % 2 == 0:
                        option = self.parseFormat(choices[i].strip())
                    else:
                        result = self.parseBody(choices[i].strip())
                        funcInner.append((option, result))
            elif funcTitle == 'random':
                funcInner = []
                choices = self.splitByPipe(funcInnerStr.strip())
                for a in choices:
                    funcInner.append(self.parseBody(a.strip()))
            funcNode = FuncNode(funcTitle, funcArgs, funcInner)
            nodes.append(funcNode)
        return BodyNode(nodes)

    def parseScript(self, scriptStr):
        """ Converts file contents string into a list of (string verb, BodyNode reaction) tuples """
        # split bodyStr into lines
        lines = scriptStr.split('\n')
        # remove indenting by stripping leading/trailing spaces from lines
        lines = [line.strip() for line in lines]
        # remove single line comments
        lines = [line for line in lines if len(line) == 0 or line[0] != '#']
        # remove end of line comments
        lines = [(line[:line.index('#')] if '#' in line else line) for line in lines]
        # join back into one string
        scriptStr = '\n'.join(lines)
        remainingInd = 0
        tuples = []
        while remainingInd < len(scriptStr):
            braceLoc = scriptStr.find("{", remainingInd)
            if braceLoc == -1:
                break
            verb = scriptStr[remainingInd:braceLoc].strip()
            closeInd = self.matchingBraceIndex(scriptStr, braceLoc + 1)
            reaction = self.parseBody(scriptStr[braceLoc+1:closeInd].strip())
            tuples.append((verb, reaction))
            remainingInd = closeInd + 1
        return tuples

    def executeBody(self, bodyNode):
        """ Evaluates a BodyNode """
        pass


if __name__ == '__main__':
    i = Interpreter()
    print(i.parseFormat("Hello @red{there}, friend. How are @bold{you} doing?"))
    print(i.parseFormat("@blue{This} is blue. But @italic{this} is italicized. And @blue{this one} is also blue."))
