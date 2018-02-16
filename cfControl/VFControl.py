import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import time
from matplotlib.animation import FuncAnimation

class VFResult:
    F = 0
    conv = 0
    circ = 0
    tv = 0

class VFData:
    x = np.double(0.0)
    y = np.double(0.0)
    z = np.double(0.0)
    xdot = np.double(0.0)
    ydot = np.double(0.0)
    xc = np.double(0.0)
    yc = np.double(0.0)
    xc_dot = np.double(0.0)
    yc_dot = np.double(0.0)
    r = np.double(1.0)
    t = np.double(0.0)
    # G=0.0
    # H=0.0
    # L=0.0
    bNormVFVectors = False
    bUseVRel = False

class AvoidOpt:
    oVFList = []
    DecayFunc = []
    UAV = []

class PlotOpt:
    bCustomRange = []
    bCustomCenter = []
    CustomNumberOfPoints = []
    DecayFunc = []
    UAV = []
    VF = []

class CircleVectorField:
    G = 1.0
    H = -1.0
    L = 1.0
    bUseVRel = False
    # vel_x = 0.0
    # vel_y = 0.0

    mCircleRadius = .25

    xc = 0.0
    yc = 0.0
    vel_x = 0.0
    vel_y = 0.0
    xc_history = []
    yc_history = []
    bUsePathFunc = False
    velPathFunc = None
    bGradientVF = False
    bLyapunovVF = False
    radFunc = None

    def __init__(obj, name_type):
        if name_type == 'Gradient':
            obj.bGradientVF = True
        elif name_type == 'Lyapunov':
            obj.bLyapunovVF = True
        else:
            print('no VF type')
            sys.exit(1)

    def GetVF_at_XY(obj, s):
        s.bNormVFVectors = s.bNormVFVectors
        s.bUseVRel = obj.bUseVRel
        s.r = obj.mCircleRadius
        s.xc = obj.xc
        s.yc = obj.yc

        if obj.bUsePathFunc == False or obj.velPathFunc is None:
            s.velx = obj.vel_x
            s.vely = obj.vel_y
        else:
            vel_v = obj.velPathFunc(s.t)
            s.velx = vel_v[0]
            s.vely = vel_v[1]

        if (obj.bGradientVF):
            V = obj.VFtv(s)
        elif (obj.bLyapunovVF):
            V['Field'] = obj.VFLyapunov(s)
        else:
            print('no VF type')
            sys.exit(1)

        return V

    def UpdatePosition(obj, t, dt, uavv):
        if (not obj.bUsePathFunc or obj.velPathFunc is None):
            # s['velx'] = obj.vel_x
            # s['vely'] = obj.vel_y
            obj.vel_x = 0
            obj.vel_y = 0
        else:
            vel_v = obj.velPathFunc(t)
            obj.vel_x = vel_v[0]
            obj.vel_y = vel_v[1]

        obj.xc = obj.xc + obj.vel_x * dt
        obj.yc = obj.yc + obj.vel_y * dt
        obj.xc_history.append(obj.xc)  # = [obj.xc_history,obj.xc]
        obj.yc_history.append(obj.yc)  # = [obj.yc_history,obj.yc]

        if (obj.radFunc is not None):
            vel_r = sqrt(uavv.x ^ 2 + uavv.y ^ 2) / sqrt(obj.vel_x ^ 2 + obj.vel_y ^ 2)
            if (vel_r == inf):
                vel_r = 1
            new_r = obj.radFunc(vel_r)
            obj.mCircleRadius = new_r
            fprintf('R->%4.2f\n', new_r)

    def SetPosition(obj, newxy):
        obj.xc = newxy[0]
        obj.yc = newxy[1]

    def PlotFieldAroundRadius(obj,opt):
        Rxx = []
        P = []
        limit = obj.mCircleRadius*1.5
        NumPoints = 0.5
        if opt.bCustomRange:
            limit = opt.bCustomRange
        if opt.CustomNumberOfPoints:
            NumPoints = opt.CustomNumberOfPoints
        if opt.bCustomCenter:
            xct = opt.bCustomCenter[1]
            yct = opt.bCustomCenter[2]
        else:
            xct = obj.xc
            yct = obj.yc
        VFUAV = []
        if opt.UAV:
            VFUAV = opt.UAV
        x_list = np.linspace(-limit, limit, NumPoints) + xct
        y_list = np.linspace(-limit, limit, NumPoints) + yct
        for i in range(0, len(x_list)):
            x = x_list[i]
            for ii in range(0, len(y_list)):
                y = y_list[ii]
                s = VFData()
                s.x = x
                s.y = y
                s.z = 0
                s.xc = obj.xc
                x.yc = obj.yc
                s.velx = obj.vel_x
                s.vely = obj.vel_y
                s.r = obj.mCircleRadius
                r_at_now = np.sqrt(np.square((x - obj.xc)) + np.square((y - obj.yc)))
                Rxx[i][ii] = r_at_now
                P[i][ii] = 1
                if opt.DecayFunc:
                    P[i][ii] = opt.DecayFunc(r_at_now)
                s.G = obj.G
                s.H = obj.H
                s.L = obj.L
                if VFUAV:
                    s.bNormVFVectors = VFUAV.bNormVFVEctors
                    uav_vel = VFUAV.GetVelocityV()
                    s.uav_vx

                if cvf.bGradientVF:
                    VF_res = cvf.VFtv(s)
                    VF_list_tv[i][ii] = VF_res.tv
                    VF_list_circ[i][ii] = VF_res.circ
                    VF_list_conv[i][ii] = VF_res.conv
                    VF_list

    def VFLyapunov(obj, s):
        x = s.x - s.xc
        y = s.y - s.yc
        rd = s.r
        r = sqrt(x ^ 2 + y ^ 2)
        u = -x * (r ^ 2 - rd ^ 2) / (r ^ 2 + rd ^ 2) - y * (2 * r * rd) / (r ^ 2 + rd ^ 2)
        v = -y * (r ^ 2 - rd ^ 2) / (r ^ 2 + rd ^ 2) + x * (2 * r * rd) / (r ^ 2 + rd ^ 2)
        V = np.array([u, v])
        return V

    def alpha1_circ(o, s):
        # alp1 = (s.x - s.xc) ^ 2 + (s.y - s.yc) ^ 2 - s.r ^ 2
        alp1 = np.square(s.x - s.xc) + np.square(s.y - s.yc) - np.square(s.r)
        return alp1

    def alpha2_circ(o, s):
        alp2 = s.z
        return alp2

    def Vconv_c(o, s):
        V1 = -o.alpha1_circ(s) * np.array([2. * (s.x - s.xc), 2. * (s.y - s.yc), 0]) / s.r
        V2 = o.alpha2_circ(s) * np.array([0, 0, 1])
        V = V1 + V2
        return V

    def Vcirc_c(o, s):
        V = np.array([2. * (s.y - s.yc), -2. * (s.x - s.xc), 0])
        return V

    def VFtv(o, s):
        Vcnv = o.G * o.Vconv_c(s)
        Vcrc = o.H * o.Vcirc_c(s)
        TV = -o.L * (o.Minv_a(s))
        if (s.bNormVFVectors):
            Vcnv = Vcnv / np.linalg.norm(Vcnv)
            if(np.linalg.norm(Vcrc) != 0 ):
                Vcrc = Vcrc / np.linalg.norm(Vcrc)
            if (np.linalg.norm(TV) != 0):
                TV = TV / np.linalg.norm(TV)
        V = VFResult
        V.conv = Vcnv
        V.circ = Vcrc
        V.tv = TV
        V.F = Vcnv + Vcrc + TV
        return V

    def Ma_(o, x, xc):
        a = 2 * (x - xc)
        return a

    def Mb_(o, y, yc):
        b = 2 * (y - yc)
        return b

    def Mp_(o, s):  # dAlphadt
        if (o.bUseVRel):
            p = 2 * (s.x - s.xc) * -(s.uav_vx - s.velx) + 2 * (s.y - s.yc) * -(s.uav_vy - s.vely)
            # p = -2 * (s.uav_vx - s.velx) * (s.x - s.xc) - 2 * (s.uav_vy - s.vely) * (s.y - s.yc)
        else:
            p = (-2.0 * s.velx * (s.x - s.xc) - 2.0 * s.vely * (s.y - s.yc)) / np.square(s.r)

        return p

    def Minv_a(o, s):
        # Mia = o.Mp_(s);
        # dAlpha1 = [o.Ma_(s.x, s.xc);0;o.Mb_(s.y, s.yc)];
        # Mia = Mia * dAlpha1 / norm(dAlpha1). ^ 2;

        a = np.array([o.Ma_(s.x, s.xc)])
        b = np.array([o.Mb_(s.y, s.yc)])
        p = np.array([o.Mp_(s)])

        # top = p/(a*a+b*b)
        # z = np.array([top]) * np.array([a,b,0])

        # Mia = (o.Mp_(s) / (np.array([(o.Ma_(s.x, s.xc) ^ 2 + o.Mb_(s.y, s.yc) ^ 2)])) * np.array([o.Ma_(s.x, s.xc),o.Mb_(s.y, s.yc),0]))

        Mia = o.Mp_(s) / (np.square(o.Ma_(s.x, s.xc)) + np.square(o.Mb_(s.y, s.yc))) * np.array(
            [o.Ma_(s.x, s.xc), o.Mb_(s.y, s.yc), 0])

        return Mia
    def GetVF_XYUV(self,t,dt,uav,IncludeUAVPos=False):
        qlimit = 2

        qstep = 50

        uavpos = uav.GetPosition()
        uavx = uavpos[0]
        uavy = uavpos[1]
        if IncludeUAVPos and (uavx > self.xc+qlimit or uavx < self.xc-qlimit) and (uavy > self.yc+qlimit or uavy < self.yc-qlimit):

            points = np.array([uavx,uavy,self.xc,self.yc])
            qlimitH = np.amax(points)+self.mCircleRadius*2
            qlimitL = np.amin(points)-self.mCircleRadius*2
            #qstep = (qlimitH-qlimitL)*2.0 / qstep
        else:
            qlimitL = -qlimit
            qlimitH = qlimit

        #print("Draw limits "+str(qlimitL) + " / " + str(qlimitH) + " - "+str(qstep))
        i = 1
        ii = 1
        VF_list = []
        xy_list = []
        Xd = []
        Yd = []
        Ud = []
        Vd = []
        for x in np.linspace(qlimitL, qlimitH, qstep):
            for y in np.linspace(qlimitL, qlimitH, qstep):
                params = VFData()
                params.x = x
                params.y = y
                params.t = t
                newVF = self.GetVF_at_XY(params)
                xy = np.array([x, y])
                VF_list.append(newVF.F)
                xy_list.append(np.array([x, y]))
                Xd.append(x)
                Yd.append(y)
                Ud.append(newVF.F[0])
                Vd.append(newVF.F[1])
        Udn = []
        Vdn = []
        for i in range(len(Ud)):
            normal = np.sqrt(np.square(Ud[i]) + np.square(Vd[i]))
            Udn.append(Ud[i] / normal)
            Vdn.append(Vd[i] / normal)

        tdata = {'x': Xd, 'y': Yd, 'u': Udn, 'v': Vdn, 'xc': self.xc, 'yc': self.yc}
        return tdata

class VFUAV:
    mPositionHistory = []
    mVelocityVHistory = []
    mHeadingHistory = []
    mTurnrate = 0.0
    uav_v_range = [1, 8]
    bVFControlHeading = False
    bVFControlVelocity = True
    bDubinsPathControl = True
    m_dt = 0
    mID = -1
    bNormVFVectors = False

    def __init__(obj, dt):
        obj.mPositionHistory = []
        obj.mVelocityVHistory = []
        obj.mHeadingHistory = []
        obj.m_dt = dt

    def GetHeading(obj):
        # print(str(length(obj.mHeadingHistory)))
        if (obj.mHeadingHistory):
            spot = len(obj.mHeadingHistory) - 1
            theta_rad = obj.mHeadingHistory[spot]
        else:
            theta_rad = float('nan')
        return theta_rad

    def GetPosition(obj):
        if (obj.mPositionHistory):
            spot = len(obj.mPositionHistory) - 1
            pos = obj.mPositionHistory[spot]
        else:
            pos = np.array([float('nan'), float('nan')])
        return pos

    def GetVelocityV(obj):
        if (obj.mVelocityVHistory):
            spot = len(obj.mVelocityVHistory) - 1
            velV = obj.mVelocityVHistory[spot]
        else:
            velV = np.array([float('nan'), float('nan')])
        return velV

    def SetPosition(obj, newPos):
        obj.mPositionHistory.append(newPos)

    def SetHeading(obj, newHeading):
        obj.mHeadingHistory.append(newHeading)

    def SetVelocityAndHeading(obj, u):
        newV = [u['vx'], u['vy']]
        newT = u['heading']
        obj.SetHeading(newT)
        obj.mVelocityVHistory.append(newV)

    def GetMaxTurnrate(obj):
        return obj.mTurnrate

    def ExportNewTurnAngleFromVF(self,new_vector,VF_obj,t):
        # current state of the vehicle
        dt = self.m_dt
        pos = new_vector['pos']
        theta = new_vector['theta']
        #theta = obj.GetHeading()
        #pos = obj.GetPosition()
        uav_x = pos[0]
        uav_y = pos[1]
        uav_v = new_vector['velocity_vec']
        #uav_v = obj.GetVelocityV()
        uav_vx = np.double(uav_v[0])
        uav_vy = np.double(uav_v[1])
        #uav_v = np.sqrt(np.square(uav_vx) + np.square(uav_vy))

        self.SetPosition(pos)
        self.SetVelocityAndHeading({'vx':uav_vx,'vy':uav_vy,'heading':theta})

        # should match getheading
        s = VFData()
        s.t = t
        s.x = uav_x
        s.y = uav_y
        s.uav_vx = uav_vx
        s.uav_vy = uav_vy
        s.bNormVFVectors = self.bNormVFVectors
        VFres = VF_obj.GetVF_at_XY(s)
        # vf_angle = atan2(VFres.F(2),VFres.F(1))
        vf_angle = np.arctan2(VFres.F[1], VFres.F[0])
        return vf_angle

    def UpdateControlFromVF(obj, VF_obj, t, opt):
        # current state of the vehicle
        dt = obj.m_dt

        theta = obj.GetHeading()
        pos = obj.GetPosition()
        uav_x = pos[0]
        uav_y = pos[1]
        uav_v = obj.GetVelocityV()
        uav_vx = np.double(uav_v[0])
        uav_vy = np.double(uav_v[1])
        uav_v = np.sqrt(np.square(uav_vx) + np.square(uav_vy))

        # should match getheading
        s = VFData()
        s.t = t
        s.x = uav_x
        s.y = uav_y
        s.uav_vx = uav_vx
        s.uav_vy = uav_vy
        s.bNormVFVectors = obj.bNormVFVectors
        VFres = VF_obj.GetVF_at_XY(s)
        U = VFres.F[0]
        V = VFres.F[1]

        if opt.oVFList:
            Uavoid = np.ones(len(opt.oVFList))
            Vavoid = np.ones(len(opt.oVFList))

            for k in range(0, len(opt.oVFList)):

                VFx = opt.oVFList[k]
                avoid = VFx.GetVF_at_XY(s)
                r_at_now = np.sqrt(np.square((uav_x-VFx.xc))+np.square((uav_y-VFx.yc)))
                P = opt.DecayFunc[k](r_at_now)
                Uavoid[k] = avoid.F[0]*P
                Vavoid[k] = avoid.F[1]*P
            U = U+np.sum(Uavoid)
            V = V+np.sum(Vavoid)

        # vf_angle = atan2(VFres.F(2),VFres.F(1))
        vf_angle = np.arctan2(V, U)

        # fprintf('%4.2f (x=%4.2f,y=%4.2f) -> VF %4.2f T %4.2f V %4.2f\n',t,uav_x,uav_y,vf_angle,theta,uav_v)
        status = '%4.2f (x=%4.2f,y=%4.2f) -> VF %4.2f T %4.2f V %4.2f' % (t, uav_x, uav_y, vf_angle, theta, uav_v)
        print(status)

        # update new position/heading/velocity
        if obj.bVFControlHeading or obj.bVFControlVelocity:
            if obj.bVFControlHeading:
                theta = vf_angle

        if obj.bDubinsPathControl and not obj.bVFControlHeading:
            turnrate = obj.GetMaxTurnrate()
            beta = vf_angle
            theta = np.arctan2(uav_vy, uav_vx)  # update AFTER the new vel (x,y)
            # needs to be used, constrains theta to +/- pi

            if abs(theta - beta) < np.pi:
                if theta - beta < 0:
                    theta = theta + turnrate * dt
                else:
                    theta = theta - turnrate * dt

            else:
                if theta - beta > 0:
                    theta = theta + turnrate * dt
                else:
                    theta = theta - turnrate * dt

        if not obj.bVFControlHeading and not obj.bVFControlVelocity and not obj.bDubinsPathControl:
            error('must have uav control type')

        uav_vx = uav_v * np.cos(theta)
        uav_vy = uav_v * np.sin(theta)
        uav_x = uav_x + uav_vx * dt
        uav_y = uav_y + uav_vy * dt
        obj.SetPosition([uav_x, uav_y])
        uo = {'vx': uav_vx, 'vy': uav_vy, 'heading': theta}
        obj.SetVelocityAndHeading(uo)

    def ComputePositionError(obj, cVF):
        pos = obj.GetPosition()
        uav_x = pos[0]
        uav_y = pos[1]
        #
        #
        #
        #
        err.dist_center = sqrt((uav_x - cVF.xc) ^ 2 + (uav_y - cVF.yc) ^ 2)
        err.dist_edge = err.dist_center - cVF.mCircleRadius






    #Q = plt.quiver(Xd, Yd, Ud, Vd, units='width')







