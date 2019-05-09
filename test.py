def inRange(index):
    try: 
        i = int(index)
        return (i < 10 and i >= 0)
    except:
        return all(x in range(0,10) for x in index)

print(inRange(0))