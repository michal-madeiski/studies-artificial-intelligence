(define (problem clean-all-rooms)
    (:domain robot-cleaner)
  
    (:objects 
        rob - robot
        r1 r2 r3 - room
    )
    
    (:init 
        (robot-at-room rob r1)
        (dirty r1)
        (dirty r2)
        (dirty r3)
    )
    
    (:goal (and 
        (clean r1)
        (clean r2)
        (clean r3)
    ))
)