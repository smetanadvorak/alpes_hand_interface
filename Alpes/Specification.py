# Field names are in French to match the Alpes Instruments' official documentation

class PREFIXES:
    ECRITURE_REGISTRE                   = bytearray([ord('W'), ord('R')])
    ECRITURE_MODE_CMD_MOTEUR            = bytearray([ord('W'), ord('1')])
    ECRITURE_CONSIGNE_TENSION_POSITION  = bytearray([ord('W'), ord('2')])
    ECRITURE_LIMITE_COURANT             = bytearray([ord('W'), ord('3')])
    
    LECTURE_REGISTRE                    = bytearray([ord('R'), ord('D')])
    LECTURE_POSITION_CODEUR             = bytearray([ord('W'), ord('3')])
    LECTURE_VITESSE_MOTEUR              = bytearray([ord('W'), ord('6')])
    TEST                                = bytearray([ord('T'), ord('S')]) # Not a part of official specification. Used only in this software for testing purposes.


class VOIES:
    ALL             = [0,1,2,3,4,5]
    POUCE_ROTATION  = 0
    POUCE           = 1
    INDEX           = 2
    MAJEUR          = 3
    ANNULAIRE       = 4
    AURICULAIRE     = 5  
   
   
def VOIE2MEMOIRE(voie):
    return 1000 * (voie + 1) 
    
    
class MODE_CMD_MOTEUR:
    STOP = 0
    POSITION = 1
    TENSION = 2


# Registers (see table "LISTE DES REGISTRES DE CONSIGNES ET DE PARAMETRAGE" of "Registre Main Robotisee.pdf")
class REGISTRES:    
    # PID-related registers
    POSITION_CODEUR             = 26
    DELAI_MODE_PI               = 6
    DELTA_MODE_PI               = 7
    COEF_P                      = 8
    COEF_I                      = 9
    COEF_D                      = 10
    MIN_SOMME_ECARTS            = 15
    MAX_SOMME_ECARTS            = 16
    ECART_POSITION              = 29
    SOMME_ECARTS                = 30
    DELTA_ECARTS                = 31
    CALCUL_P                    = 35
    CALCUL_I                    = 36
    CALCUL_D                    = 37
    
    # Control-related registers
    MODE_CMD_MOTEUR             = 0
    CONSIGNE_TENSION_POSITION   = 1
    
    CONSIGNE_POSITION_MIN       = 11
    CONSIGNE_POSITION_MAX       = 12
    
    POSITION_MIN_ATTEINTE       = 38
    POSITION_MAX_ATTEINTE       = 39
    
    # Motor current control registers
    LIMITE_COURANT              = 2
    LIMITE_COURANT_DEFAUT       = 3
    
    MIN_SORTIE_PWM              = 13
    MAX_SORTIE_PWM              = 14
    SORTIE_PWM                  = 33
    
    # Angular velocity registers
    DIR_MOTEUR_CODEUR           = 19 # Note: Seems to contain 0b0..011 disregarding the direction of motor rotation.
    TEMPS_CALCUL_VITESSE        = 20 
    EMPLACEMENT_DIR_MOT_CODEUR  = 25
    VITESSE_MOTEUR              = 27
    
    # General registers
    VERSION                     = 41
    ID_DROITE_GAUCHE            = 24
    
    def __str__(self):
        attributes = [s for s in dir(self) if not s.startswith('__') and not callable(getattr(self, s))]
        s = '\n'
        for attr in attributes:
            s += '%s = %d\n' % (attr.ljust(25), getattr(self, attr))
        return s



# A standalone register with address 100, does not belong to any 'voie' (motor channel).
REGISTRE_INITIALISATION            = 100


# Some constants
MAXIMAL_THUMB_ADDUCTION            = 21000
MAXIMAL_THUMB_FLEXION              = 19000
MAXIMAL_FINGER_FLEXION             = 43000
MAXIMAL_MOTOR_POSITIONS            = [MAXIMAL_THUMB_ADDUCTION] + [MAXIMAL_THUMB_FLEXION] + [MAXIMAL_FINGER_FLEXION] * 4
MINIMAL_MOTOR_POSITIONS            = [0 ,0, 0, 0, 0, 0]


# Some parameters from motor specification (DCX10L EB KL 12V):
class MOTORSPEC:
    REDUCTION           = 256           # Gear reduction ratio
    COUNTS_PER_TURN     = 32            # Number of encoder counts per turn (before reduction)
    MAXIMAL_ABSOLUTE_TENSION    = 11.5  # [V]
    MAX_CONTINUOUS_CURRENT      = 0.211 # [A]
  
  
# Some parameters of hand's current control circuit (see 'Description Main Robotique.pdf'),
# chapter 7.Systemes de controle du courant moteur.
class CONTROLE_COURANT:
    COEFFICIENT_CNA     = 3.3 / 65535 #Converts value of LIMITE_COURANT to Amperes. 
    LIMITE_COURANT_DEFAUT = 750    
    #LIMITE_COURANT_MAX  = int(MOTORSPEC.MAX_CONTINUOUS_CURRENT / COEFFICIENT_CNA) #Equal to 4190. Never try to reach it or go beyond.
    LIMITE_COURANT_MAX  = LIMITE_COURANT_DEFAUT # Actually, hand protects itself from writing larger values to LIMITE_COURANT register.
    
  