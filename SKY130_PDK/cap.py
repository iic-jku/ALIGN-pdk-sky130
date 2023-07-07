import math
from align.primitive.default.canvas import DefaultCanvas
from align.cell_fabric.generators import *
from align.cell_fabric.grid import *

import logging
logger = logging.getLogger(__name__)

class CapGenerator(DefaultCanvas):

    def __init__(self, pdk):
        super().__init__(pdk)
        ##################################################
        ## not in use
        self.m3n = self.addGen( Wire( 'm3n', 'CapMIMLayer', 'v',
                                     clg=UncoloredCenterLineGrid( pitch=self.pdk['M3']['Pitch'], width=self.pdk['M3']['Width']),
                                     spg=EnclosureGrid(pitch=self.pdk['M2']['Pitch'], stoppoint=self.pdk['V2']['VencA_H'] + self.pdk['M2']['Width']//2, check=False)))
        
        self.m5_offset = self.pdk['CapMIMLayer']['Enclosure'] + self.pdk['CapMIMContact']['Enclosure'] + self.pdk['CapMIMContact']['WidthX']//2
        self.m5n = self.addGen(Wire( 'm5n', 'M5', 'v',
                                     clg=UncoloredCenterLineGrid( pitch=2*self.pdk['Cap']['m5Width'], width=self.pdk['Cap']['m5Width'], offset=self.m5_offset),
                                     spg=EnclosureGrid(pitch=self.pdk['M4']['Pitch']//2, stoppoint=self.pdk['CapMIMContact']['Enclosure'], offset=0, check=False)))

        self.Cboundary = self.addGen( Region( 'Cboundary', 'Cboundary', h_grid=self.m2.clg, v_grid=self.m1.clg))

        
        
        clg_mim = UncoloredCenterLineGrid( pitch=2, width=2)

        self.CapMIMC = self.addGen( Region( 'CapMIMC', 'CapMIMContact', h_grid=clg_mim, v_grid=clg_mim))
        self.CapMIM = self.addGen( Region( 'CapMIM', 'CapMIMLayer', h_grid=clg_mim, v_grid=clg_mim))
        #self.CapMIM_bottom = self.addGen( Region( 'CapMIMBottomLayer', 'M4', h_grid=clg_mim, v_grid=clg_mim))

        self.v4_region = self.addGen(Region('v4R', 'M1', h_grid=clg_mim, v_grid = clg_mim))
        self.v2_region = self.addGen(Region('v2R', 'V2', h_grid=clg_mim, v_grid = clg_mim))
        self.v1_region = self.addGen(Region('v1R', 'V1', h_grid=clg_mim, v_grid = clg_mim))
        ##################################################


        #define usefull grids
        mySPG = EnclosureGrid(pitch=self.m2.spg.period, stoppoint=0, offset=0) #grid with m2.spg period
        mySPG_v = EnclosureGrid(pitch=self.m2.clg.period, stoppoint=0, offset=0) #grid with m2.clg period

        #define wires for the pins
        self.myM5 = self.addGen(Wire("myM5", "M5", "v", clg=UncoloredCenterLineGrid( pitch=self.m2.spg.period, width=self.pdk['M5']['Width'], offset=0), spg=mySPG_v))
        self.myM4 = self.addGen(Wire("myM4", "M4", "h", clg=UncoloredCenterLineGrid( pitch=self.m2.clg.period, width=self.pdk['M4']['Width'], offset=0), spg=mySPG))
        self.myM3 = self.addGen(Wire("myM3", "M3", "v", clg=UncoloredCenterLineGrid( pitch=self.m2.spg.period, width=self.pdk['M3']['Width'], offset=0), spg=mySPG_v))
        self.myM2 = self.addGen(Wire("myM2", "M2", "h", clg=UncoloredCenterLineGrid( pitch=self.m2.clg.period, width=self.pdk['M2']['Width'], offset=0), spg=mySPG))
        
        #define vias for the pins
        self.v4_x = self.addGen( Via( 'v4_x', 'V4',
                                        h_clg=self.myM4.clg, v_clg=self.myM5.clg,
                                        WidthX=self.v4.WidthX, WidthY=self.v4.WidthY,
                                        h_ext=self.v4.h_ext, v_ext=self.v4.v_ext))
        self.v3_x = self.addGen( Via( 'v3_x', 'V3',
                                        h_clg=self.myM4.clg, v_clg=self.myM3.clg,
                                        WidthX=self.v3.WidthX, WidthY=self.v3.WidthY,
                                        h_ext=self.v3.h_ext, v_ext=self.v3.v_ext))
        self.v2_x = self.addGen( Via( 'v2_x', 'V2',
                                        h_clg=self.myM2.clg, v_clg=self.myM3.clg,
                                        WidthX=self.v2.WidthX, WidthY=self.v2.WidthY,
                                        h_ext=self.v2.h_ext, v_ext=self.v2.v_ext))

    def addCap(self, length, width):
        x_length = int(length)
        y_length = int(width)

        logger.debug(f"x_length: {x_length}")
        logger.debug(f"y_length: {y_length}")

        m2_period_x = self.myM2.spg.period #M2 grid distance x
        m2_period_y = self.myM2.clg.period #M2 grid distance y
        
        logger.debug(f"M2 period x: {m2_period_x}")
        logger.debug(f"M2 period y: {m2_period_y}")

        pin_length_x_min = x_length + 2*self.pdk["CapMIMLayer"]["Enclosure"] + 2*self.pdk["Cap"]["m4Pitch"] #mimimum pin length 
        

        pin_length_x = ((math.ceil(pin_length_x_min/m2_period_x)+1)//2)*2*m2_period_x #make sure pin_length_x and pin_length_x/2 is divisible by m2_period_x 
        
        n_m2_pin_x = pin_length_x//m2_period_x
        
        logger.debug(f"pin_length_x = {pin_length_x}")
        logger.debug(f"n_m2_pin_x = {n_m2_pin_x}")

        pin_distance_y_min = y_length +  2*self.pdk["CapMIMLayer"]["Enclosure"] + 2*self.pdk["Cap"]["m4Pitch"] + self.pdk["M4"]["Width"] #minimum pin distance
        pin_distance_y = ((math.ceil(pin_distance_y_min/m2_period_y)+1)//2)*2*m2_period_y #make sure pin_distance_y and pin_distance_y/2 is divisible by m2_period_y

        n_m2_pin_dist_y = pin_distance_y//m2_period_y

        n_m5 = math.floor(x_length/self.pdk["M5"]["Width"])

        logger.debug(f"pin_distance_y_min = {pin_distance_y_min}")
        logger.debug(f"pin_distance_y = {pin_distance_y}")
        logger.debug(f"n_m2_pin_dist_y = {n_m2_pin_dist_y}")
        
        #M2 h
        #M3 v
        #M4 h
        #M5 v

        ########################################################
        ### Generate the contacts
        #Plus contact
        #horizontal
        self.addWire(self.myM2, "PLUS", 0, (0,-1), (n_m2_pin_x,1), netType='pin')
        self.addVia(self.v2_x, "PLUS", n_m2_pin_x//2, 0)
        self.addWire(self.myM3, "PLUS", n_m2_pin_x//2, (-1,-1), (1,1))
        self.addVia(self.v3_x, "PLUS", n_m2_pin_x//2, 0)
        self.addWire(self.myM4, "PLUS", 0, (n_m2_pin_x//2-1,-1), (n_m2_pin_x//2+1,1))
        self.addVia(self.v4_x, "PLUS", n_m2_pin_x//2, 0)
        self.addWire(self.myM5, "PLUS", n_m2_pin_x//2, (-1,-1), (1,1))

        for n in range(1,n_m5//2):
            n_m = n_m2_pin_x//2-n*self.pdk["M5"]["Width"]//m2_period_x-self.pdk["M5"]["Width"]//m2_period_x//2
            n_p = n_m2_pin_x//2+n*self.pdk["M5"]["Width"]//m2_period_x+self.pdk["M5"]["Width"]//m2_period_x//2
            
            self.addVia(self.v2_x, "PLUS", n_m, 0)
            self.addWire(self.myM3, "PLUS", n_m, (-1,-1), (1,1))
            self.addVia(self.v3_x, "PLUS", n_m, 0)
            self.addWire(self.myM4, "PLUS", 0, (n_m-1,-1), (n_m+2,1))
            self.addVia(self.v4_x, "PLUS", n_m, 0)
            self.addWire(self.myM5, "PLUS", n_m, (-1,-1), (1,1))

            self.addVia(self.v2_x, "PLUS", n_p, 0)
            self.addWire(self.myM3, "PLUS", n_p, (-1,-1), (1,1))
            self.addVia(self.v3_x, "PLUS", n_p, 0)
            self.addWire(self.myM4, "PLUS", 0, (n_p-2,-1), (n_p+1,1))
            self.addVia(self.v4_x, "PLUS", n_p, 0)
            self.addWire(self.myM5, "PLUS", n_p, (-1,-1), (1,1))


        #Minus contact
        #horizontal
        self.addWire(self.myM2, "MINUS", n_m2_pin_dist_y, (0,-1), (n_m2_pin_x,1), netType='pin')
        self.addVia(self.v2_x, "MINUS", n_m2_pin_x//2, n_m2_pin_dist_y)
        self.addWire(self.myM3, "MINUS", n_m2_pin_x//2, (n_m2_pin_dist_y-1,-1), (n_m2_pin_dist_y+1,1))
        self.addVia(self.v3_x, "MINUS", n_m2_pin_x//2, n_m2_pin_dist_y)
        self.addWire(self.myM4, "MINUS", n_m2_pin_dist_y, (n_m2_pin_x//2-1,-1), (n_m2_pin_x//2+1,1))

        for n in range(1,n_m5//2):
            n_m = n_m2_pin_x//2-n*self.pdk["M5"]["Width"]//m2_period_x-self.pdk["M5"]["Width"]//m2_period_x//2
            n_p = n_m2_pin_x//2+n*self.pdk["M5"]["Width"]//m2_period_x+self.pdk["M5"]["Width"]//m2_period_x//2
            
            self.addVia(self.v2_x, "MINUS", n_m, n_m2_pin_dist_y)
            self.addWire(self.myM3, "MINUS", n_m, (n_m2_pin_dist_y-1,-1), (n_m2_pin_dist_y+1,1))
            self.addVia(self.v3_x, "MINUS", n_m, n_m2_pin_dist_y)
            self.addWire(self.myM4, "MINUS", n_m2_pin_dist_y, (n_m-1,-1), (n_m+2,1))

            self.addVia(self.v2_x, "MINUS", n_p, n_m2_pin_dist_y)
            self.addWire(self.myM3, "MINUS", n_p, (n_m2_pin_dist_y-1,-1), (n_m2_pin_dist_y+1,1))
            self.addVia(self.v3_x, "MINUS", n_p, n_m2_pin_dist_y)
            self.addWire(self.myM4, "MINUS", n_m2_pin_dist_y, (n_p-2,-1), (n_p+1,1))

            

        ###
        ############################################################
        ### Place the MIM Cap
        #MIM Cap
        clg_mim = UncoloredCenterLineGrid( pitch=2, width=2) #grid with 2nm spacing
        mimRegion = Region( 'CapMIM', 'CapMIMLayer', h_grid=clg_mim, v_grid=clg_mim) #region for the MIM cap
        mimContRegion = Region( 'CapMIMCont', 'CapMIMContact', h_grid=clg_mim, v_grid=clg_mim) #region for the MIM top contact
        mimBottomRegion = Region( 'CapMIMBottom', 'M4', h_grid=clg_mim, v_grid=clg_mim) #region for the MIM bottom plate 
        mimTopRegion = Region( 'CapMIMBottom', 'M5', h_grid=clg_mim, v_grid=clg_mim) #region for the MIM top contact to pin

        mim_start_x = pin_length_x//2-x_length//2 #startpoint x
        mim_start_y = pin_distance_y//2-y_length//2 #startpoint y

        mim_end_x = mim_start_x + x_length #endpoint x
        mim_end_y = mim_start_y + y_length #endpoint y
    

        if n_m5 > 1:
            top_cont_start_x = mim_start_x
            top_cont_end_x = mim_end_x
        else:
            top_cont_start_x = (n_m2_pin_x//2*m2_period_x-self.pdk["M5"]["Width"]//2)
            top_cont_end_x = (n_m2_pin_x//2*m2_period_x+self.pdk["M5"]["Width"]//2)
            
        top_cont_start_y = -self.pdk["M5"]["Width"]//2
        top_cont_end_y = mim_end_y

        logger.debug(f"top_cont_start_x = {top_cont_start_x}, mim_start_x = {mim_start_x}")

        if top_cont_start_x > mim_start_x and top_cont_end_x < mim_end_x:
            cont_start_x = top_cont_start_x + self.pdk["CapMIMContact"]["Enclosure"]
            cont_end_x = top_cont_end_x - self.pdk["CapMIMContact"]["Enclosure"]
            cont_end_y = top_cont_end_y - self.pdk["CapMIMContact"]["Enclosure"]
        else:
            cont_start_x = mim_start_x + self.pdk["CapMIMContact"]["Enclosure"]
            cont_end_x = mim_end_x - self.pdk["CapMIMContact"]["Enclosure"]
            cont_end_y = mim_end_y - self.pdk["CapMIMContact"]["Enclosure"]

        cont_start_y = mim_start_y + self.pdk["CapMIMContact"]["Enclosure"]
        
         

        self.addRegion(mimRegion, "TOP", mim_start_x//2, mim_start_y//2, (mim_end_x)//2, (mim_end_y)//2)
        
        self.addRegion(mimContRegion, "TOP", (cont_start_x)//2,
                                            (cont_start_y)//2,
                                            (cont_end_x)//2,
                                            (cont_end_y)//2 )
        
        self.addRegion(mimTopRegion, "TOP", (top_cont_start_x)//2, 
                                            (top_cont_start_y)//2,
                                            (top_cont_end_x)//2,
                                            (top_cont_end_y)//2)
        
        self.addRegion(mimBottomRegion, "BOTTOM", (mim_start_x-self.pdk["CapMIMLayer"]["Enclosure"])//2, 
                                                (mim_start_y - self.pdk["CapMIMLayer"]["Enclosure"])//2,
                                                (mim_start_x+x_length+self.pdk["CapMIMLayer"]["Enclosure"])//2,
                                                (pin_distance_y+self.pdk["M4"]["Width"]//2)//2)
        

        save_margin_cap_y = math.ceil(600/m2_period_y) #ToDo generalize, #save margin to other blocks
        save_margin_cap_x = math.ceil(1000/m2_period_x)

        #Place boundaries
        self.addRegion( self.boundary, 'Boundary', -2-save_margin_cap_x, -2-save_margin_cap_y, n_m2_pin_x+save_margin_cap_x+2, n_m2_pin_dist_y+save_margin_cap_y+2)
        self.addRegion( self.Cboundary, 'CBoundary', -2-save_margin_cap_x, -2-save_margin_cap_y, n_m2_pin_x+save_margin_cap_x+2, n_m2_pin_dist_y+save_margin_cap_y+2)
        
        logger.debug( f"Computed Boundary: {self.terminals[-1]} {self.terminals[-1]['rect'][2]} {self.terminals[-1]['rect'][2]%80}")

