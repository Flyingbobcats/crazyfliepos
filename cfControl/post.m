
clc
clear
close all

filename = uigetfile('.txt');
% disp(filename)
DATA = importfile(filename,1,10000000);

% retrieving UAV position from DATA and storing it in 'position'
position(:,1) = DATA(:,16); % x coordinates
position(:,2) = DATA(:,18); % y coordinates
position(:,3) = DATA(:,20); % z coordinates
yaw_rate = DATA(:,24);
yaw_sp = DATA(:,8);

% retrieving time from DATA
t = DATA(:,2);

% retrieving waypoint position from DATA and storing it in 'waypoint'
waypoint(:,1) = DATA(:,10);
waypoint(:,2) = DATA(:,12);
waypoint(:,3) = DATA(:,14);

% storing unique waypoints in 'wpts'
wpts = unique(waypoint,'rows');

% plot of UAV path with waypoints
figure
hold on
plot3(position(:,1),position(:,2),position(:,3))            % plotting the UAV path
% plot3(wpts(:,1),wpts(:,2),wpts(:,3),'--')    % plotting the waypoints
xlabel('x');
ylabel('y');
zlabel('z');
axis equal
grid on
view([45,45]);

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






