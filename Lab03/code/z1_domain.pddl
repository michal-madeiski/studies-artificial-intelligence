(define (domain transport)
    (:requirements :strips :typing :numeric-fluents :durative-actions :negative-preconditions)
    
    (:types 
        city location physobj - object
        package vehicle - physobj
        truck airplane ship - vehicle
        truck-loading-point airport harbour - location
    )
    
    (:predicates 
        (loc-in-city ?l - location ?c - city)
        (veh-at-loc ?v - vehicle ?l - location)
        (pkg-at-loc ?p - package ?l - location)
        (pkg-in-veh ?p - package ?v - vehicle)
        (conn-road ?l1 ?l2 - location)
        (conn-air ?l1 ?l2 - location)
        (conn-water ?l1 ?l2 - location)
    )
    
    (:functions 
        (drive-time ?l1 ?l2 - location)
        (fly-time ?l1 ?l2 - location)
        (sail-time ?l1 ?l2 - location)
        (drive-cost ?l1 ?l2 - location)
        (fly-cost ?l1 ?l2 - location)
        (sail-cost ?l1 ?l2 - location)
        (total-cost)
    )
    
    (:durative-action load
        :parameters (?v - vehicle ?p - package ?l - location)
        :duration (= ?duration 2)
        :condition (and 
            (at start (veh-at-loc ?v ?l))
            (at start (pkg-at-loc ?p ?l))
        )
        :effect (and 
            (at start (not (pkg-at-loc ?p ?l)))
            (at end (pkg-in-veh ?p ?v))
        )
    )
      
    (:durative-action unload
        :parameters (?v - vehicle ?p - package ?l - location)
        :duration (= ?duration 2)
        :condition (and 
            (at start (veh-at-loc ?v ?l))
            (at start (pkg-in-veh ?p ?v))
        )
        :effect (and 
            (at start (not (pkg-in-veh ?p ?v)))
            (at end (pkg-at-loc ?p ?l))
        )
    )
      
    (:durative-action drive
        :parameters (?v - truck ?l1 ?l2 - location)
        :duration (= ?duration (drive-time ?l1 ?l2))
        :condition (and 
            (at start (veh-at-loc ?v ?l1))
            (over all (conn-road ?l1 ?l2))
        )
        :effect (and 
            (at start (not (veh-at-loc ?v ?l1)))
            (at end (veh-at-loc ?v ?l2))
            (at end (increase (total-cost) (drive-cost ?l1 ?l2)))
        )
    )
      
    (:durative-action fly
        :parameters (?v - airplane ?l1 ?l2 - airport)
        :duration (= ?duration (fly-time ?l1 ?l2))
        :condition (and 
            (at start (veh-at-loc ?v ?l1))
            (over all (conn-air ?l1 ?l2))
        )
        :effect (and 
            (at start (not (veh-at-loc ?v ?l1)))
            (at end (veh-at-loc ?v ?l2))
            (at end (increase (total-cost) (fly-cost ?l1 ?l2)))
        )
    )
      
    (:durative-action sail
        :parameters (?v - ship ?l1 ?l2 - harbour)
        :duration (= ?duration (sail-time ?l1 ?l2))
        :condition (and 
            (at start (veh-at-loc ?v ?l1))
            (over all (conn-water ?l1 ?l2))
        )
        :effect (and 
            (at start (not (veh-at-loc ?v ?l1)))
            (at end (veh-at-loc ?v ?l2))
            (at end (increase (total-cost) (sail-cost ?l1 ?l2)))
        )
    )
)