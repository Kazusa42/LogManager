import re
import statistics


if __name__ == '__main__':
   
    filename = r"C:\Users\a5149517\Desktop\Automation_tools\log\300cm.log"
    with open(filename, encoding='utf8', newline='') as f:
        i = 0
        buffa=[]
        for row in f:
            row = str(row) 
            if i % 2 == 1:
                
                distancedata = (row[110:])
                distance = re.sub(r'\D', '', distancedata) 


                
                try:
                    decimalDis=int(distance)

                    calValue = decimalDis   
                    if calValue != 65535:
                        buffa.append(calValue)
                    
                    print(calValue) 
                except:
                    continue
                
                
                
            i += 1
        N   = len(buffa)
        MAX = max(buffa)
        MIN = min(buffa)
        midian = statistics.median_high(buffa)
        ave = statistics.mean(buffa)
        print("N",N,"Max",MAX,"Min",MIN,"midian",midian,"AVE",ave)
