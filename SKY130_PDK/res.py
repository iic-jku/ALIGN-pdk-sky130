from align.primitive.default.canvas import DefaultCanvas
from align.cell_fabric.generators import *
from align.cell_fabric.grid import *

import math

import logging
logger = logging.getLogger(__name__)

class ResGenerator(DefaultCanvas):

    def __init__(self, pdk, fin, finDummy):
        super().__init__(pdk)
        self.finsPerUnitCell = fin + 2*finDummy
        # TODO: Generalize these
        self.m1res = self.addGen( Wire( 'm1res', 'M1', 'v',
                                     clg=ColoredCenterLineGrid( colors=['c1','c2'], pitch=self.pdk['Cap']['m1Pitch'], width=self.pdk['Cap']['m1Width']),
                                     spg=EnclosureGrid( pitch=self.pdk['M2']['Pitch'], stoppoint=self.pdk['V1']['VencA_L'] +self.pdk['Cap']['m2Width']//2, check=True)))

        self.m1res2 = self.addGen( Wire( 'm1res2', 'M1', 'h',
                                     clg=ColoredCenterLineGrid( colors=['c1','c2'], pitch=self.pdk['M2']['Pitch'], width=self.pdk['Cap']['m1Width']),
                                     spg=EnclosureGrid( pitch=self.pdk['Cap']['m1Pitch'], stoppoint=self.pdk['Cap']['m1Width']//2, check=False)))

        self.m2res = self.addGen( Wire( 'm2res', 'M2', 'h',
                                     clg=ColoredCenterLineGrid( colors=['c1','c2'], pitch=self.pdk['M2']['Pitch'], width=self.pdk['Cap']['m2Width']),
                                     spg=EnclosureGrid( pitch=self.pdk['Cap']['m1Pitch'], stoppoint=self.pdk['V1']['VencA_H'] + self.pdk['Cap']['m1Width']//2, check=False)))

        self.m2res2 = self.addGen( Wire( 'm2res2', 'M2', 'h',
                                      clg=ColoredCenterLineGrid( colors=['c1','c2'], pitch=self.pdk['Cap']['m2Pitch'], width=self.pdk['Cap']['m2Width']),
                                      spg=EnclosureGrid( pitch=self.pdk['Cap']['m1Pitch'], stoppoint=self.pdk['V1']['VencA_H'] + self.pdk['Cap']['m1Width']//2)))

        self.m3res = self.addGen( Wire( 'm3res', 'M3', 'v',
                                     clg=ColoredCenterLineGrid( colors=['c1','c2'], pitch=self.pdk['Cap']['m3Pitch'], width=self.pdk['Cap']['m3Width']),
                                     spg=EnclosureGrid(pitch=self.pdk['M2']['Pitch'], stoppoint=self.pdk['V2']['VencA_H'] + self.pdk['Cap']['m2Width']//2, check=True)))

        self.v1res = self.addGen( Via( 'v1res', 'V1',
                                        h_clg=self.m2res.clg, v_clg=self.m1res.clg,
                                        WidthX=self.v1.WidthX, WidthY=self.v1.WidthY,
                                        h_ext=self.v1.h_ext, v_ext=self.v1.v_ext))
        self.v2res = self.addGen( Via( 'v2res', 'V2', h_clg=self.m2res.clg, v_clg=self.m3res.clg,
                                        WidthX=self.v2.WidthX, WidthY=self.v2.WidthY,
                                        h_ext=self.v2.h_ext, v_ext=self.v2.v_ext))

        #definitions for sky130_fd_pr__res_high_po_0p35
        mySPG = EnclosureGrid(pitch=self.m2.spg.period, stoppoint=0, offset=0) #grid with m2.spg period
        mySPG_v = EnclosureGrid(pitch=self.m2.clg.period, stoppoint=0, offset=0) #grid with m2.clg period

        mySPG_M1_v = EnclosureGrid(pitch=350, stoppoint=0, offset=-175) #grid with m2.clg period
        self.myPoly0p35 = self.addGen(Wire('poly0p35', 'Pc', 'h', clg=UncoloredCenterLineGrid( pitch=self.m2.clg.period, width=350, offset=0), spg=mySPG))
        self.myM2 = self.addGen(Wire('myM2', 'M2', 'h', clg=UncoloredCenterLineGrid( pitch=self.m2.clg.period, width=self.pdk["M2"]["Width"], offset=0), spg=mySPG))
        self.myM1 = self.addGen(Wire('myM1', 'M1', 'h', clg=UncoloredCenterLineGrid( pitch=self.m2.clg.period, width=350, offset=0), spg=mySPG))
        self.myM1_v = self.addGen(Wire('myM1_v', 'M1', 'v', clg=UncoloredCenterLineGrid( pitch=self.m2.spg.period, width=350, offset=175), spg=mySPG_M1_v))
        
        self.myV0 = self.addGen( Via( 'myV0', 'V0',
                                        h_clg=self.myPoly0p35.clg, v_clg=self.myM1_v.clg,
                                        WidthX=self.v1.WidthX, WidthY=self.v1.WidthY,
                                        h_ext=self.v1.h_ext, v_ext=self.v1.v_ext))
        
        self.myV1 = self.addGen( Via( 'myV1', 'V1',
                                        h_clg=self.myM2.clg, v_clg=self.myM1_v.clg,
                                        WidthX=self.v1.WidthX, WidthY=self.v1.WidthY,
                                        h_ext=self.v1.h_ext, v_ext=self.v1.v_ext))

        clg_mim = UncoloredCenterLineGrid( pitch=2, width=2) #grid with 2nm spacing
        self.p_res_boundary = self.addGen(Region("PRES_boundary", "Npc", h_grid=clg_mim, v_grid=clg_mim))
        self.p_impl_boundary = self.addGen(Region("PIMPL_boundary", "Pselect", h_grid=clg_mim, v_grid=clg_mim))
        self.urpm_boundary = self.addGen(Region("Urpm_boundary", "Urpm", h_grid=clg_mim, v_grid=clg_mim))
        self.p_res_region = self.addGen(Region("PRES", "PRes", h_grid=clg_mim, v_grid=clg_mim))
        self.Rboundary = self.addGen( Region( 'Rboundary', 'Rboundary', h_grid=self.m2.clg, v_grid=self.m1.clg))

    def addResArray(self, x_cells, y_cells, height, unit_res):

        for x in range(x_cells):
            for y in range(y_cells):
                self._addRes(x, y, height, unit_res, (x == x_cells-1) and (y == y_cells-1))

    
    def _addRes(self, x, y, height, unit_res, draw_boundary=True):
        
        l = round(unit_res / 2000 * 350)

        m2_period_x = self.myM2.spg.period

        logger.debug(f"x={x}, y={y}, h={height}, unit_res={unit_res}, l={l}")

        n_vias_per_pin = 6
        poly_length = math.ceil((2*n_vias_per_pin * m2_period_x + l)/m2_period_x)*m2_period_x

        n_poly = poly_length//m2_period_x

        self.addWire(self.myPoly0p35, "POLY", 0, (0,-1), (n_poly,1))
        #self.addWire(self.myM1, "PLUS", 0, (0,-1), (6,1))
        self.addWire(self.myM2, "PLUS", 0, (0,-1), (n_vias_per_pin,1),netType="pin")
        #self.addWire(self.myM1, "MINUS", 0, (n_poly-6,-1), (n_poly,1))
        self.addWire(self.myM2, "MINUS", 0, (n_poly-n_vias_per_pin,-1), (n_poly,1),netType="pin")
        
        
        
        for n in range(n_vias_per_pin):
            self.addWire(self.myM1_v, "PLUS", n, (0,-1), (1,1))
            self.addVia(self.myV0, "PLUS", n, 0)
            self.addVia(self.myV1, "PLUS", n, 0)
        
        for n in range(n_vias_per_pin):
            self.addWire(self.myM1_v, "MINUS", n_poly-n-1, (0,-1), (1,1))
            self.addVia(self.myV0, "MINUS", n_poly-n-1, 0)
            self.addVia(self.myV1, "MINUS", n_poly-n-1, 0)

        clg_mim = UncoloredCenterLineGrid( pitch=2, width=2) #grid with 2nm spacing
        li_region = Region("Licon", "M1", h_grid=clg_mim, v_grid=clg_mim)
        
        
        self.addRegion(li_region, "PLUS", 0, -175//2, (n_vias_per_pin*m2_period_x)//2, 175//2)
        self.addRegion(self.p_res_region, "PRES", (n_vias_per_pin*m2_period_x-60)//2, -175//2, (n_vias_per_pin*m2_period_x+l+60)//2, 175//2)
        self.addRegion(li_region, "MINUS", (n_vias_per_pin*m2_period_x+l)//2, -175//2, (n_poly*m2_period_x)//2, 175//2)
        
        
        
        self.addRegion(self.p_res_boundary, None, 0, -175//2, (n_poly*m2_period_x)//2, 175//2)
        self.addRegion(self.p_impl_boundary, None, 0, -175//2, (n_poly*m2_period_x)//2, 175//2)
        self.addRegion(self.urpm_boundary, None, 0, -175//2, (n_poly*m2_period_x)//2, 175//2)

        self.addRegion(self.boundary, "boundary", -2,-2, n_poly+2,2)