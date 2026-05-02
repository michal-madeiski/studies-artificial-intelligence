(define (domain robot-cleaner)
    (:requirements :strips :typing)
    
    (:types 
        robot room - object
    )
    
    (:predicates 
        (robot-at-room ?r - robot ?p - room)
        (dirty ?p - room)
        (clean ?p - room)
    )
    
    (:action move
        :parameters (?r - robot ?from - room ?to - room)
        :precondition (and 
            (robot-at-room ?r ?from)
        )
        :effect (and 
            (not (robot-at-room ?r ?from))
            (robot-at-room ?r ?to)
        )
    )
    
    (:action clean
        :parameters (?r - robot ?p - room)
        :precondition (and 
            (robot-at-room ?r ?p)
            (dirty ?p)
        )
        :effect (and 
            (not (dirty ?p))
            (clean ?p)
        )
    )
)