
clc
clear
close all

filename = uigetfile('.txt');
obsFile = uigetfile('.out');
% disp(filename)

xfile = uigetfile('XVF.out');
yfile = uigetfile('YVF.out');
ufile = uigetfile('UVF.out');
vfile = uigetfile('VVF.out');

[time,x,y,z,yaw,x_sp,y_sp,z_sp,yaw_sp] = importfile1(filename,1,10000000);
obsData = OBSimportfile(obsFile);
XS = VFDataimportfile(xfile);
YS = VFDataimportfile(yfile);
US = VFDataimportfile(ufile);
VS = VFDataimportfile(vfile);

% retrieving UAV position from DATA and storing it in 'position'
position(:,1) = x; % x coordinates
position(:,2) = y; % y coordinates
position(:,3) = z; % z coordinates
yaw_rate = yaw;
yaw_sp = yaw_sp;

% retrieving time from DATA
t = time;

% retrieving waypoint position from DATA and storing it in 'waypoint'
waypoint(:,1) = x_sp;
waypoint(:,2) = y_sp;
waypoint(:,3) = z_sp;

% storing unique waypoints in 'wpts'
wpts = unique(waypoint,'rows');

theta = linspace(0,2*pi,length(obsData(1,:)));
circXs = obsData(3,1)*cos(theta);
circYs = obsData(3,1)*sin(theta);


% plot of UAV path with waypoints
figure
hold on
quiver(XS,YS,US,VS)
plot(position(:,1),position(:,2),'LineWidth',3)            % plotting the UAV path
% plot3(wpts(:,1),wpts(:,2),wpts(:,3),'--')    % plotting the waypoints
plot(obsData(1,:)+circXs,obsData(2,:)+circYs)
xlabel('x');
ylabel('y');
axis equal
grid on

% x position
figure
subplot(4,1,1)
hold on
plot(t,position(:,1)) % plotting x position versus time
xlabel('time (seconds)');
ylabel('x (meters)');
plot(t,waypoint(:,1),'--r','linewidth',2); % plotting waypoint x path

% y position
subplot(4,1,2)
hold on
plot(t,position(:,2)) % plotting y position versus time
xlabel('time (seconds)');
ylabel('y (meters)');
plot(t,waypoint(:,2),'--r','linewidth',2); % plotting waypoint y path

% z position
subplot(4,1,3)
hold on
plot(t,position(:,3)) % plotting y position versus time
xlabel('time (seconds)');
ylabel('z (meters)');
plot(t,waypoint(:,3),'--r','linewidth',2); % plotting waypoint y path

subplot(4,1,4)
hold on
plot(t,yaw_rate) % plotting y position versus time
xlabel('time (seconds)');
ylabel('yaw');
plot(t,yaw_sp,'--r','linewidth',2); % plotting waypoint y path






