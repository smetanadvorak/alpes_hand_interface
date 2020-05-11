from AlpesHand import AlpesHand
from AlpesSpecification import *
import numpy as np
import numpy.matlib


class Grasp:
    def __init__(self, command_nodes, trajectory_nodes):
        if command_nodes[0] != 0 or command_nodes[-1] != 1: 
            raise ValueError('Specified GRASP object is incorrectly implemented.')
        self.command_nodes = command_nodes
        self.trajectory_nodes = trajectory_nodes
        self.final_position = [self.trajectory_nodes[-1,i] for i in range(self.trajectory_nodes.shape[1])]
        
    def interpolate(self, x1, x2, y1, y2, x):
        #print('Grasp.interpolate():',x1, x2, y1, y2, x)
        return y1 + np.true_divide(y2-y1, x2-x1) * (x-x1) # Same as return y1 + (y2-y1)/(x2-x1) * x, but Python2-friendly.
        
    def get_trajectory_point(self, x): 
        if x < 0 or x > 1:
            raise ValueError('Value for proportional control should be 0 < x < 1. No command applied, running script is aborted.')               
        for i in range(1, len(self.command_nodes)):
            if x >= self.command_nodes[i-1] and x <= self.command_nodes[i]:
                point = self.interpolate(  self.command_nodes[i-1],       self.command_nodes[i], 
                                           self.trajectory_nodes[i-1,:],  self.trajectory_nodes[i,:], x)
                return point.tolist()
        


class AlpesProsthesis(AlpesHand):
    def __init__(self, port = None):
        super().__init__(port)
        self.grasp = None

        
    def proportional_control_position(self, x):
        if self.grasp is None:
            print('Error: Before requesing proportional control, set the desired grasp using .set_grasp() method.')
        else:
            point  =  self.grasp.get_trajectory_point(x) 
            point  =  [int(point[i] * MAXIMAL_MOTOR_POSITIONS[i]) for i in range(len(point))] #From normalised values to the motor angle values:
            self.write_positions(point)
            
            
    def proportional_control_current(self, x):
        if self.grasp is None:
            print('Error: Before requesing proportional control, set the desired grasp using .set_grasp() method.')
        else:            
            # Regulate motion by changing the motors' current limit. PID of the hand will almost always 
            # draw maximal current if it is limited below 750 (Alpes' default value of current limit).
            point    =  self.grasp.get_trajectory_point(x)
            current  =  [int(point[i] * CONTROLE_COURANT.LIMITE_COURANT_DEFAUT) for i in range(len(point))]
            print(x, point, current)
            self.set_current_limits(current)
            # Always aim to reach final position
            # self.write_positions([int(self.grasp.final_position[i] * MAXIMAL_MOTOR_POSITIONS[i]) for i in range(len(self.grasp.final_position))])
            self.proportional_control_position(1)

    def set_grasp(self, grasp):
        self.gestures = None
        self.grasp = grasp
        self.proportional_control_position(0)
        
        
    def set_gesture(self, gesture):
        self.grasp = None
        self.set_current_limits()
        self.gesture = [int(gesture[i] * MAXIMAL_MOTOR_POSITIONS[i]) for i in range(len(gesture))]
        self.write_positions(self.gesture)
   


class GRASPS:
    # Grasps are continuous motions of the robotic hand that are spanned across the values 
    # of input parameter that is bound to [0,1].
    
    # Some grasps (e.g. LATERAL) can be described by hand's initial position (when input parameter is 0)
    # and its final position (when the parameter is 1). The continuum of positions in 
    # between these two can be calculated by mapping the values of the input parameter to 
    # the motor angles. This code uses linear mapping (see 'Grasp.interpolate()' method).
    
    # Some grasps (e.g. CYLINDRICAL) are described by three and more positions, to assure
    # correct placement of the thumb (e.g., above other fingers in CYLINDRICAL).
    
    # Positions are described in 'trajectory_nodes' matrix: each row is a positional command to
    # the six motors of the hand. Values of the input parameter for which these positions are 
    # specified in 'command_nodes' list. All values are normalised to 1, where position=1 
    # means that the motor should reach its maximal rotation angle specified in AlpesSpecification.MAXIMAL_MOTOR_POSITIONS
    
    # To implement new grasps, add them to this class, following the format below:
    CYLINDRICAL = Grasp(command_nodes = [0.0, 
                                         0.8, 
                                         1.0],
                        trajectory_nodes = 
                        np.array([  [1.0,      0.05,   0.15,   0.15,   0.15,   0.20],
                                    [1.0,      0.2,    0.8,    0.8,    0.8,    0.80],
                                    [1.0,      0.75,   0.90,   0.90,   0.90,   0.90]]))
                                    
    LATERAL     = Grasp(command_nodes = [0.0, 
                                        #0.5, 
                                         1.0],
                        trajectory_nodes = 
                        np.array([  [0.0,      0.05,   0.15,   0.15,   0.15,   0.20],
                                    #[0.0,      0.45,   0.45,   0.45,   0.45,   0.45],
                                    [0.0,      0.90,   0.90,   0.90,   0.90,   0.90]]))
                                    
                                                                 
    PINCH       = Grasp(command_nodes = [0.0, 
                                         0.6, 
                                         1.0],
                        trajectory_nodes = 
                        np.array([  [1.0,      0.05,   0.15,   0.15,   0.15,   0.20],
                                    [1.0,      0.45,   0.45,   0.15,   0.15,   0.20],
                                    [1.0,      0.90,   0.90,   0.20,   0.20,   0.25]]))    
                                    
                                                                    
class GESTURES:
    OPEN            = [0.00, 0.00, 0.00, 0.00, 0.00, 0.00]
    REST            = [0.25, 0.15, 0.17, 0.20, 0.20, 0.25]
    CLOSE           = [0.25, 0.50, 0.90, 0.90, 0.90, 0.90]
    LATERAL         = [0.00, 0.50, 0.90, 0.90, 0.90, 0.90]
    OK              = [0.50, 0.15, 0.70, 0.30, 0.20, 0.15]
    PUNK            = [0.50, 0.20, 0.20, 0.90, 0.90, 0.20]
    VICTORY         = [0.50, 0.30, 0.10, 0.20, 0.90, 0.90]
    ONE             = [0.75, 0.30, 0.10, 0.80, 0.85, 0.90]
    TWO             = [0.75, 0.30, 0.10, 0.20, 0.85, 0.90]
    THREE           = [0.75, 0.30, 0.10, 0.00, 0.10, 0.90]
    FOUR            = [1.00, 0.30, 0.10, 0.00, 0.10, 0.15]
    FIVE            = [0.00, 0.00, 0.00, 0.00, 0.00, 0.00]
      



    
    