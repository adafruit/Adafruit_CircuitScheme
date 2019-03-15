;;; Scheme Interpreter in CircuitPython
;;; Based on Lispy.py (c) Peter Norvig, 2010; See http://norvig.com/lispy2.html
;;;
;;; Adafruit invests time and resources providing this open source code.
;;; Please support Adafruit and open source hardware by purchasing
;;; products from Adafruit!
;;;
;;; Written by Dave Astels for Adafruit Industries
;;; Copyright (c) 2019 Adafruit Industries
;;; Licensed under the MIT license.
;;;
;;; All text above must be included in any redistribution.
;;;
;;; Lists support library
;;; Adds the rich set of standard Scheme list functions.  Only the
;;; basic list functions are builtin

(define (nth k l)
  (if (eq? k 0)
      (car l)
      (nth (- k 1) (cdr l))))

(define (list-ref l k)
  (nth k l))

;; Remove any elements of l for which p evaluates to #t

(define (remove a-predicate a-list)
  (define (inner a-predicate a-list accumulated)
    (cond ((null? a-list)
           accumulated)
          ((a-predicate (car a-list))
           (inner a-predicate (cdr a-list) accumulated))
          (#t
           (inner a-predicate (cdr a-list) (append accumulated (list (car a-list)))))))
  (inner a-predicate a-list '()))

;; Remove shorthands for eq? and equal?

(define (delq element l)
  (remove (lambda (x) (eq? x element)) l))

(define (delete element l)
  (remove (lambda (x) (equal? x element)) l))

;; list decomposition functions

(define (caar l) (car (car l)))
(define (cadr l) (car (cdr l)))
(define (cdar l) (cdr (car l)))
(define (cddr l) (cdr (cdr l)))

(define (caaar l) (car (car (car l))))
(define (caadr l) (car (car (cdr l))))
(define (cadar l) (car (cdr (car l))))
(define (caddr l) (car (cdr (cdr l))))
(define (cdaar l) (cdr (car (car l))))
(define (cdadr l) (cdr (car (cdr l))))
(define (cddar l) (cdr (cdr (car l))))
(define (cdddr l) (cdr (cdr (cdr l))))

(define (caaaar l) (cdr (car (car (car l)))))
(define (caaadr l) (cdr (car (car (cdr l)))))
(define (caadar l) (cdr (car (cdr (car l)))))
(define (caaddr l) (cdr (car (cdr (cdr l)))))
(define (cadaar l) (cdr (cdr (car (car l)))))
(define (cadadr l) (cdr (cdr (car (cdr l)))))
(define (caddar l) (cdr (cdr (cdr (car l)))))
(define (cadddr l) (cdr (cdr (cdr (cdr l)))))
(define (cdaaar l) (cdr (car (car (car l)))))
(define (cdaadr l) (cdr (car (car (cdr l)))))
(define (cdadar l) (cdr (car (cdr (car l)))))
(define (cdaddr l) (cdr (car (cdr (cdr l)))))
(define (cddaar l) (cdr (cdr (car (car l)))))
(define (cddadr l) (cdr (cdr (car (cdr l)))))
(define (cdddar l) (cdr (cdr (cdr (car l)))))
(define (cddddr l) (cdr (cdr (cdr (cdr l)))))

;; Return the last item in a list

(define (last l)
  (cond ((null? l)
         '())
        ((null? (cdr l))
         (car l))
        (#t (last (cdr l)))))

;; return evereything except the last item.
;; This returns a new list

(define (except-last l)
  (define (inner l accumulated)
    (if (null? (cdr l))
        accumulated
        (inner (cdr l) (append accumulated (list (car l))))))
  (cond ((or (null? l)
             (null? (cdr l)))
         '())
        (#t
         (inner l '()))))

;; Reverse a list

(define (reverse l)
  (define (inner l accumulated)
    (if (null? l)
        accumulated
        (inner (cdr l) (cons (car l) accumulated))))
  (inner l '()))

;; Mapping over a list

(define (map procedure l)
  (define (inner procedure l accumulated)
    (if (null? l)
        accumulated
        (inner procedure (cdr l) (append accumulated (list (procedure (car l)))))))
  (inner procedure l '()))

;; Evaluate procedure on each element of l in order
;; result is unspecified

(define (for-each procedure l)
  (unless (null? l)
      (procedure (car l))
      (for-each procedure (cdr l))))

;; Left associative reduction

(define (reduce-left procedure initial l)
  (define (inner procedure accumulated l)
    (if (null? l)
        accumulated
        (inner procedure (procedure accumulated (car l)) (cdr l))))
  (cond ((null? l)
         initial)
        ((null? (cdr l))
         (car l))
        (#t (inner procedure (car l) (cdr l)))))

(define reduce reduce-left)

(define (reduce-right procedure initial l)
  (define (inner procedure accumulated l)
    (if (null? l)
        accumulated
        (inner procedure (procedure (last l) accumulated (reverse (except-last l))))))
  (cond ((null? l)
         initial)
        ((null? (cdr l))
         (car l))
        (#t (inner procedure (last l) (reverse (except-last l))))))
