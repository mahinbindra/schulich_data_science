import random
import math

TRIALS = 10000
totalTime = 0
totalTimeSquared = 0

# Should we calculate and report the SE?
CALCULATE_SE = False

for trial in range(TRIALS):
    
    # Determine the type of package and sets the first service time
    packageProb = random.random()                           # Generates a random number between 0 and 1
    
    # If the x-ray scan reveals that the package is a food item. 
    if packageProb < 0.3:                   
        packageType = "FOOD"
        serviceTime = random.lognormvariate(1.4, 0.5)       # Generates a lognormal random variate
    # If the x-ray scan reveals that the package is a weapon.
    elif packageProb < 0.4:
        packageType = "WEAPON"
        serviceTime = random.lognormvariate(1.9, 0.4)       # Generates a lognormal random variate
    # If the x-ray scan reveals that the package is another item.
    else:
        packageType = "OTHER"
        serviceTime = random.lognormvariate(1.1, 0.1)       # Generates a lognormal random variate
        
    # Given the package type is known, augment the service time if it is suspicious as it must be disposed of.    
    if packageType == "FOOD":
        if(random.random() < 0.2):                          # If suspicious, increase service time for food
            serviceTime += random.gammavariate(18,3)        
    elif packageType == "WEAPON":                           # If suspicious, increase service time for weapons
        if(random.random() < 0.4):
            serviceTime += random.gammavariate(26,6)
    elif packageType == "OTHER":                            # If suspicious, increase service time for other
        if(random.random() < 0.06):
            serviceTime += random.gammavariate(22,7)                               
    totalTime += serviceTime                                # Add the service time to the summation
    totalTimeSquared += serviceTime*serviceTime             # Add the squared service time to the summation
    
# Calculate the average time over all trials and print the result 
averageTime = 1.0*totalTime/TRIALS
print("The average service time is %2.2f minutes." % averageTime)    

if CALCULATE_SE:
    # Calculate the standard error over all trials and print the result 
    variance = 1.0/(TRIALS-1)*totalTimeSquared - 1.0*TRIALS/(TRIALS-1)*averageTime*averageTime
    standardDeviation = math.sqrt(variance)              
    standardError = math.sqrt(1.0*variance/TRIALS)
    print("The standard deviation is %2.2f minutes." % standardDeviation)
    print("The standard error is %2.2f minutes." % standardError)
    print("The 90%% confidence interval is (%2.2f, %2.2f)." % (averageTime -  1.645*standardError , averageTime + 1.645*standardError))
    print("The 95%% confidence interval is (%2.2f, %2.2f)." % (averageTime -  1.96*standardError , averageTime + 1.96*standardError))
    print("The 99%% confidence interval is (%2.2f, %2.2f)." % (averageTime -  2.575*standardError , averageTime + 2.575*standardError))