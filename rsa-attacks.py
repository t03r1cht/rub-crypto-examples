from math import gcd
from math import sqrt
from math import floor
import primefac
from fractions import Fraction

def factorize_n(n, e, d, a=2):
    """
    Factor both primes p, q from n using the naive approach.
    
    n: the modulus to factor into p, q (p, q prime)
    e: the public RSA key
    d: the private RSA key
    a: a random number from the natural numbers excluding 0 (Z_n*)

    See RUB script page 88
    """
    
    # check if a coprime n (gcd(a,n) = 1)
    if not gcd(a,n) == 1:
        print("a, n not coprime")
        return
    else:
        print("a, n coprime")

    # factor e*d-1 into 2^s * u
    factors=get_prime_factors(e*d-1)

    # check if 2 is a prime factor, if not we can't continue with attack
    if not 2 in factors:
        print("2 not a prime factor of e*d-1")
        return

    s=factors[2]
    # pop key 2, for easier computation of u
    factors.pop(2)
    # calculate u (multiplication of all prime factors except 2)
    u = 1
    for key in factors:
        u *= key**factors[key]
    
    print("s ==>", s)
    print("u ==>", u)

    # compute a^u mod n
    a_u=a**u%n
    
    # compute j_i for each j in (0, ..., s-1): j_i = gcd((a^u)^2^j - 1,n) = p IFF p NEQ 1, p NEQ n
    p=0
    for i in range(s):
        j_i=gcd(a_u**2**i-1,n)
        if not j_i==1 and not j_i==n:
            p=j_i
            break
    
    if p==0:
        print("could not find p in iterations, attack failed")
        return

    # compute q using n and p
    q=n//p
    if not p*q==n:
        print("n was not correctly factored")
        return

    print()
    print("p ==>", p)
    print("q ==>", q)

def rsa_attack_small_e(p_1, p_2, p_3):
    """
    Takes 3 tuples with (n_i, e_i, c_i) (attack on 3 parties)
    c_i must be equal for all 3 tuples
    """
    # unwind tuples 
    n_1=p_1[0]
    e_1=p_1[1]
    c_1=p_1[2]

    n_2=p_2[0]
    e_2=p_2[1]
    c_2=p_2[2]

    n_3=p_3[0]
    e_3=p_3[1]
    c_3=p_3[2]

    # check if the public key is the same for all 3 parties
    if not e_1==e_2==e_3:
        print("public key e not equal for all 3 parties, cannot perform attack")
        return
    
    # use the CRT (by hand) to solve the system of congruences computing c (ciphertext that satisfies all 3 congruences)
    # c = c_1 mod n_1
    # c = c_2 mod n_2
    # c = c_3 mod n_3
    
    # modulus to reduce final c
    N=n_1*n_2*n_3

    # find x_1, x_2, x_3 so that:
    # x_1: n_2 * n_3 * x_1 = 1 mod n_1 --> c_1 * n_2 * n_3 * x_1 = c_1 * 1 = c_1 mod n_1
    # x_2: n_3 * n_1 * x_2 = 1 mod n_2 --> c_2 * n_3 * n_1 * x_2 = c_2 * 1 = c_2 mod n_2
    # x_3: n_1 * n_2 * x_3 = 1 mod n_3 --> c_3 * n_1 * n_2 * x_3 = c_3 * 1 = c_3 mod n_3
    #
    # in other words: x_1 is the modular multiplicative inverse from n_2 * n_3 (mod n_1)

    x_1 = pow(n_2*n_3, -1, n_1)
    x_2 = pow(n_3*n_1, -1, n_2)
    x_3 = pow(n_1*n_2, -1, n_3)
    print()
    print("x_1 ==>", x_1)
    print("x_2 ==>", x_2)
    print("x_3 ==>", x_3)
    
    # assemble the result of the CRT
    c = c_1 * n_2 * n_3 * x_1
    c += c_2 * n_3 * n_1 * x_2
    c += c_3 * n_1 * n_2 * x_3
    # reduce mod N
    c=c%N
    print("c ==>", c)

    # since c = m^e (mod n_1*n_2*n_3), compute the e-th root of c
    # all public keys (e) are equal
    e=e_1
    print("m ==>", round(c**(1/float(e))))

def rsa_attack_small_d(n,e):
    """
    Requires a modulus n=p*q, p, q prime and the public RSA key e

    Relies heavily on the fact that edg=k*floor((edg/k))+g and p+q=-floor(edg/k)+n+1
    """
    pass

def get_prime_factors(x):
    """
    Factorizes a give number into a list of prime factors
    """
    return primefac.factorint(x)
    

def number_to_cf(n,d=1):
    """
    Requires a numerator and denominator: n/d
    Calculate the continued fraction of the given number (ger.: kettenbruchentwicklung)

    n/d = <q_0, ... , q_m>
    n/1 = <n>
    """
    # initialize the lists that hold the q_i, r_i values we need to compute the continued fractions
    q_i=[]
    r_i=[]

    if d==0:
        print("cant divide by zero")
        return

    # if the give fraction is a natural number (denominator is 1)
    if d==1:
        q_i.append(n)
        return q_i

    # init q_0, r_0
    q_i.append(int(floor(Fraction(n,d))))
    # use double index to access the un-floored q_0 (0: un-floored, 1: floored)
    r_i.append(Fraction(n,d)-q_i[0])
    
    # TODO: exactly when does it stop?
    # runs until q_i=i
    #
    # in other words: continue, until q_i is an integer ==> float(Fraction(n,d)).is_integer()
    # we calculate the next iteration generally as:
    # q_i = floor(1/(r_(i-1)))
    # r_i = 1/(r_(i-1)) - q_i
    i = 1
    while True:
        # index 0 is the un-floored previous q_i
        q = floor(Fraction(1, r_i[i-1]))
        q_i.append(int(q))

        # perform exit condition check, if it fails, continue with computation of r
        if i == q:
            break
        r = Fraction(1, r_i[i-1]) - Fraction(q, 1)
        r_i.append(r)

        i+=1
        
    return q_i

if __name__ == '__main__':
    #factorize_n(n=667,e=3, d=411)
    # rsa_attack_small_e(p_1=(289,3,120),
    #                    p_2=(529,3,413),
    #                    p_3=(319,3,213))
    print(number_to_cf(4,11))
    print(number_to_cf(n=5))
    print(number_to_cf(1234,57))
