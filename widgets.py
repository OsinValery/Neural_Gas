
from kivy.uix.widget import Widget
from kivy.graphics import Line, Point, Color
from kivy.properties import StringProperty, BooleanProperty, NumericProperty

class DataPresenter(Widget):
    def __init__(self,data, **kwargs):
        super().__init__(**kwargs)
        self.max_x = 0
        self.min_x = 0
        self.max_y = 0
        self.min_y = 0
        if data != []:
            self.max_x = data[0][0]
            self.min_x = self.max_x
            self.max_y = data[0][1]
            self.min_y = self.max_y
            for point in data:
                if point[0] > self.max_x:
                    self.max_x = point[0]
                if point[0] < self.min_x:
                    self.min_x = point[0]
                if point[1] > self.max_y:
                    self.max_y = point[1]
                if point[1] < self.min_y:
                    self.min_y = point[1]
        diameter = max(abs(self.max_x), abs(self.min_x), abs(self.max_y), abs(self.min_y))
        self.scale = 1
        # size[0] = size[1] !!!!
        if diameter > self.size[0] / 2:
            self.scale = self.size[0] / 2 / diameter

    def build(self, gas, data):
        self.canvas.clear()
        with self.canvas:
            Color(0,0,0, 0.5)
            Line(points=[0, self.size[1] / 2, self.size[0], self.size[1] / 2])
            Line(points=[self.size[0] / 2, 0, self.size[0] / 2, self.size[1]])
            Color(0,0,1,0.2)
        # draw data
        points = []
        for point in data:
            points += [
                self.scale * point[0] + self.size[0] / 2, 
                point[1] * self.scale + self.size[1] / 2
            ]
            if (len(points) == 1024):
                self.canvas.add(Point(points=points,pointsize=1))
                points = []
        self.canvas.add(Point(points=points,pointsize=1))
        # draw connections
        with self.canvas:
            Color(0,1,0,5)
        for connection in gas.connections:
            neuron1, neuron2 = connection.neuron1, connection.neuron2
            x1,y1 = neuron1.pos
            x2,y2 = neuron2.pos
            self.canvas.add(Line(
                points = [
                    x1 * self.scale + self.size[0] / 2, 
                    y1 * self.scale + self.size[1] / 2, 
                    x2 * self.scale + self.size[0] / 2, 
                    y2 * self.scale + self.size[1] / 2
                ],
                width = 1.5
            ))
        
        # draw neurons
        points = []
        for neuron in gas.neurons:
            x,y = neuron.pos
            points += [self.size[0] / 2 + x * self.scale, self.size[1] / 2 + y * self.scale]
        with self.canvas:
            Color(1,0,0,1)
            Point(points=points, pointsize=2.5) 



class RightMenu(Widget):
    def __init__(self,gas,inc_all_connections, **kwargs):
        super().__init__(**kwargs)
        self.gas = gas
        self.disable = False
        self.inc_all_connections = inc_all_connections
    
    def educate(self, arg = ...):
        self.parent.start_education()
    
    def reset_model(self, arg=...):
        if self.parent.education:
            return
        if self.gas.neurons != []:
            self.gas.reset_state()
            self.parent.drawInterface(0,0, 'press button')

    def build(self,epoch, epochs, step, status = ''):
        self.clear_widgets()
        self.add_widget(RightWidget(
            pos=self.pos,
            size=self.size,
            status = status,
            neurons = int(len(self.gas.neurons)),
            max_neurons = str(self.gas.max_neurons),
            epoch = str(epoch),
            epochs = str(epochs),
            step = str(step),
            max_connection_age = str(self.gas.max_age),
            birth_step = str(self.gas.birth_step),
            winner_step = str(self.gas.winner_step),
            neighbour_step = str(self.gas.neighbour_step),
            d_error = str(self.gas.d_error),
            birth_error = str(self.gas.birth_error),
            inc_all_connections = self.inc_all_connections,
            init_neurons = str(self.gas.init_neurons),
            disable=self.disable
        ))

class RightWidget(Widget):
    # see in widgets.kv
    status = StringProperty()
    neurons = NumericProperty()
    max_neurons = StringProperty()
    epoch = StringProperty()
    epochs = StringProperty()
    step = StringProperty()
    max_connection_age = StringProperty()
    birth_step = StringProperty()
    winner_step = StringProperty()
    neighbour_step = StringProperty()
    d_error = StringProperty()
    birth_error = StringProperty()
    inc_all_connections = BooleanProperty()
    disable = BooleanProperty()
    init_neurons = StringProperty()

    def reset_model(self, arg=...):
        self.parent.reset_model()
    
    def educate(self, arg=...):
        self.parent.educate()
    
    def change_neurons_max(self):
        text = self.ids.neurons.text
        if (text != '' and text != '-' and not text.isspace()):
            self.parent.gas.max_neurons = int(text)
            if (self.parent.gas.max_neurons <= 0):
                self.ids.neurons.text = '2'
                self.parent.gas.max_neurons = 2
        else:
            self.parent.gas.max_neurons = 2

    def change_epochs_max(self):
        text = self.ids.epochs.text
        epochs = 5
        if (text != '' and text != '-' and not text.isspace()):
            epochs = int(text)
            if (epochs <= 0):
                self.ids.epochs.text = '5'
                epochs = 5
        else:
            epochs = 5
        self.parent.parent.change_epochs(epochs)
    
    def change_age_max(self):
        text = self.ids.age.text
        age = 5
        if (text != '' and text != '-' and not text.isspace()):
            age = int(text)
            if (age <= 0):
                self.ids.epochs.text = '5'
                age = 5
        else:
            age = 5
        self.parent.gas.max_age = age

    def neurons_birth(self):
        text = self.ids.birth_count.text
        birth = 90
        if (text != '' and text != '-' and not text.isspace()):
            birth = int(text)
            if (birth <= 0):
                self.ids.epochs.text = '90'
                birth = 90
        else:
            birth = 90
        self.parent.gas.birth_step = birth

    def change_vinner_step(self):
        text = self.ids.winner_step.text
        step = 0.07
        if (text != '' and text != '-' and not text.isspace()):
            step = float(text)
            if (step < 0 or step > 1):
                step = 0.07
                self.ids.winner_step.text = '0.07'
        else:
            step = 0.07
        self.parent.gas.winner_step = step

    def change_neighbour_step(self):
        text = self.ids.neighbour_step.text
        step = 0.02
        if (text != '' and text != '-' and not text.isspace()):
            step = float(text)
            if (step < 0 or step > 1):
                step = 0.02
                self.ids.neighbour_step.text = '0.02'
        else:
            step = 0.02
        self.parent.gas.neighbour_step = step
    
    def change_d_error(self):
        text = self.ids.d_error.text
        d_error = 0.95
        if (text != '' and text != '-' and not text.isspace()):
            d_error = float(text)
            if (d_error < 0 or d_error > 1):
                d_error = 0.95
                self.ids.d_error.text = '0.95'
        else:
            d_error = 0.95
        self.parent.gas.d_error = d_error

    def change_birth_error(self):
        text = self.ids.birth_error.text
        birth_error = 0.5
        if (text != '' and text != '-' and not text.isspace()):
            birth_error = float(text)
            if (birth_error < 0 or birth_error > 1):
                birth_error = 0.5
                self.ids.d_error.text = '0.5'
        else:
            birth_error = 0.5
        self.parent.gas.birth_error = birth_error

    def change_init_neurons(self):
        text = self.ids.init_neurons.text
        init = 2
        if (text != '' and text != '-' and not text.isspace()):
            init = int(text)
            if (init < 0 ):
                init = 2
                self.ids.init_neurons.text = '2'
        else:
            init = 2
        self.parent.gas.init_neurons = init
    
    def change_oldness(self, value):
        res = value == 'All'
        self.inc_all_connections = res
        self.parent.parent.change_inc_all_connection(res)


