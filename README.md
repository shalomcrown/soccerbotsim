# Soccer

The idea is to make a framework for generating strategies for soccer bots, in a simulated environment.

In other words:
- I want to build soccer bots but I don't know how to develop their strategies
- In order to do that and have an open competition, I need a simulation environment
- The simulator should be a federation, like HLA to allow others to connect their strategies

To do this, we need a set of communication protocols and definitions.

- There will be brokers that will distribute the messages between the simulators.
- There will be referees that manage the simulation and enforce the rules of the game, and the laws of physics.

For now, there is a rectangular pitch. The simulation is two dimensional,
where players are considered to be circles. Each player has a fixed mass and radius.
The ball is also a circle with a mass. Players and the ball have coefficients of friction against the ground and
are simulated to be sliding. The referee may or may not simulate axial rotation of the ball, but this is internal.

The idea is to make the simulation totally modular so that many kinds of components can be developed independently.

The players move by specifying a force vector. The referee issues messages containing
the positions, remaining potential energy, and velocity vectors of the players and the ball.

To simulate player tiring, each player is assigned a potential energy value. The referee may limit movement 
when players' potential energy is low.

These messages are broadcast.The movement requests from teams to the manager are private.

Observers could be participants that just display the match or supply sound effects for instance.

Fouls: A collision between players in a given radius from the ball is a foul. Apart from that, offsides can occur.

The referee can declare a stoppage for a free kick or offside, or half time or end of match.

The game state messages give game time and simluation time of day, the scores of the teams, positions and velocities 
of players etc.

The game start message allots each team a half of the pitch. The teams respond with a ready message giving the starting
coordinates of each player. This message is also used after a goal. The referee may check the validity of the positions.

The kickoff message allows the player that is kicking off to start moving until it makes contact with the ball, when 
all movement will be allowed.


There will be the following kinds of messages:

<ul>
<li> Game setup - this will be supplied to each simulator that connects (after the referee) (broadcast)
	<ul>
	<li>Coordinates of the pitch, positions of goals etc. </li>
	<li>Number of players per team                        </li>
	<li>Total mass of players                             </li>
	<li>Total area of players                             </li>
	<li>Maximum motive force of players                   </li>
	<li>Total potential energy of players (J) 			  </li>
	<li>Coefficient of friction of player vs ground       </li>
	<li>Coefficient of friction of ball vs ground         </li>
	<li>Duration of game								</li>
	<li>Simulation speed as a fraction of real-time </li>
	</ul>
</li>

<li>Participant setup message is broadcast (?) by a participant
	<ul>
	<li>Participant type: Team, observer, referee</li>
	<li>Participant name</li>
	</ul>
</li>

<li> To this, the simulators respond with lists of players.

<li>For each player the following should be specified</li>
	<ul>
	<li>Jersey number</li>
	<li>Name</li>
	<li>Mass</li>
	<li>Potential energy</li>
	<li>Active (or on the bench)</li>
	<li>Game start coordinates</li>
	</ul>
</li>
<li> Time: The 
</li>
</ul>


Having suggested some of that, let's look towards implementation.

There are two topics to address here:
 - The message queue / broker
 - The message format
 
For broker, we're going to use MQTT and for message format: Protobuf

Ubuntu offers a number of MQTT servers: Mosquitto, EJabberd
So we're going with Mosquitto. It doesn't really matter what server you use, but I need to test them for other reasons.

