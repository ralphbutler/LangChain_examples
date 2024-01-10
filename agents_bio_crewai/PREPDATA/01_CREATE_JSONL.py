split_value = "{'ModelSEED ID':"

outfile = open('combined_cpdrxn.jsonl', 'w')
with open('combined_cpdrxn.txt', 'r') as infile: 
    for (idx,line) in enumerate(infile):
        line = line.strip()
        if not line:
            continue
        sline = line.split(split_value)
        line = split_value + sline[1]
        start = 0
        end = start
        brace_count = 1
        while end < len(line) and brace_count > 0:
            end += 1
            if end >= len(line):
                print("DBG",idx,line)
                exit(0)
            if line[end] == '{':
                brace_count += 1
            elif line[end] == '}':
                brace_count -= 1
        if start != -1 and end != -1:
            line = line[start:end+1]
            line = line.replace("'",'"')
            line = line.replace("None",'""')
            outfile.write(line[start:end+1] + '\n')
