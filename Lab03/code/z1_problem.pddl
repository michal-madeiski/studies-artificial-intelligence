(define (problem transport-city1-city2)
    (:domain transport)
      
    (:objects
        city1 city2 - city
        
        tlp1 - truck-loading-point
        air1 - airport
        har1 - harbour
        
        tlp2 - truck-loading-point
        air2 - airport
        har2 - harbour
        
        truck1 - truck
        truck2 - truck
        plane - airplane
        ship - ship
        
        pkg - package
    )
    
    (:init
        (loc-in-city tlp1 city1) (loc-in-city air1 city1) (loc-in-city har1 city1)
        (loc-in-city tlp2 city2) (loc-in-city air2 city2) (loc-in-city har2 city2)
        
        (pkg-at-loc pkg tlp1)
        (veh-at-loc truck1 tlp1)
        (veh-at-loc truck2 tlp2)
        (veh-at-loc plane air1)
        (veh-at-loc ship har1)
        
        (conn-road tlp1 air1)
        (conn-road tlp1 har1)
        
        (conn-road tlp2 air2) (conn-road air2 tlp2) 
        (conn-road tlp2 har2) (conn-road har2 tlp2) 
        
        (conn-road tlp1 tlp2)
        (conn-air air1 air2)
        (conn-water har1 har2)
        
        (= (total-cost) 0)
    
        (= (drive-time tlp1 air1) 4)  (= (drive-cost tlp1 air1) 10)
        (= (drive-time tlp1 har1) 5)  (= (drive-cost tlp1 har1) 12)
        
        (= (drive-time tlp2 air2) 4)  (= (drive-cost tlp2 air2) 10)
        (= (drive-time air2 tlp2) 4)  (= (drive-cost air2 tlp2) 10)
        
        (= (drive-time tlp2 har2) 5)  (= (drive-cost tlp2 har2) 12)
        (= (drive-time har2 tlp2) 5)  (= (drive-cost har2 tlp2) 12)
        
        (= (drive-time tlp1 tlp2) 200) (= (drive-cost tlp1 tlp2) 500)
        (= (fly-time air1 air2) 50)    (= (fly-cost air1 air2) 1000)
        (= (sail-time har1 har2) 300)  (= (sail-cost har1 har2) 250)
    )
    
    (:goal (and 
        (pkg-at-loc pkg tlp2)
    ))

    (:metric minimize (total-time))
)