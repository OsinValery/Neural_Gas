import random
import gas
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.graphics import Line, Color, Rectangle
from kivy.base import Builder
from kivy.core.window import Window
from kivy.clock import Clock 
from kivy.utils import platform
from widgets import *

window_height = 500
menu_width = 250


interactive_step = 100
# отвечает за замедление процесса
# не ставьте слишком маленькое значение
# иначе графика не будет успевать отрисовывать интерфейс
# если ваше устройство позволяет, можно уменьшить
time_per_step = 0.05

data = []

# fill data here

n = 2 ** 16

side = 150
for i in range(n):
    data.append((random.uniform(-side,side), random.uniform(-side,side)))

# default values
max_neurons = 50
# must be >= 2
init_neurons = 2

winner_step = 0.07
neighbour_step = 0.02

max_connection_age = 30

# уменьшать ошибку, умножая на коэф <= 1
d_error = 0.95

# создавать нейрон каждые n шагов, если можно
birth_step = 90

# уменьшать ошибку соседей нового нейрона, умножая на коэф <= 1
birth_error = 0.5

epochs = 5
# boolean value
inc_all_connections = 0

class Education(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.size = window_size
        self.education = False
        with self.canvas:
            Color(1,1,1,1)
            Rectangle(size=self.size)
            Color(1,0,0,1)
            Line(points=[self.size[1],0, self.size[1], self.size[1]], width = 1)
        self.rightMenu = RightMenu(Gas,inc_all_connections=inc_all_connections, pos=[self.size[1], 0], size = [menu_width, self.size[1]])
        self.dataPresenter = DataPresenter(data, size = [self.size[1]] * 2, pos = [0,0])    
        self.drawInterface(0,0, 'press button')


    def start_education(self, arg=...):
        if self.education:
            return
        self.education = True
        self.rightMenu.disable = True
        self.iterator = Gas.education_iterator(
            data, 
            epochs=epochs, 
            interactive=0, 
            itetation_step=interactive_step, 
            increment_all=inc_all_connections
        )
        self.timer = Clock.schedule_once(self.education_step, time_per_step)
    
    def education_step(self, dt):
        try:
            epoch, step = self.iterator.__next__()
            status = 'educating'
            self.timer = Clock.schedule_once(self.education_step, time_per_step)
            self.education = False
        except Exception as e:
            self.timer.cancel()
            epoch = epochs - 1
            step = Gas.step
            status = 'finished'
            self.rightMenu.disable = False
            classes = Gas.divide_by_classes()
            for el in classes:
                print(len(el))
        self.drawInterface(epoch=epoch + 1, step=step, status=status)

    def drawInterface(self,epoch, step, status = ''):
        self.clear_widgets()
        self.dataPresenter.size = [self.size[1]] * 2
        self.rightMenu.size =  [menu_width, self.size[1]] 
        self.rightMenu.build(epoch,epochs,step,status)
        self.dataPresenter.build(Gas, data)
        self.add_widget(self.dataPresenter)
        self.add_widget(self.rightMenu)
    
    def change_epochs(self, new):
        global epochs
        epochs = new
    
    def change_inc_all_connection(self, value):
        global inc_all_connections
        inc_all_connections = value
        self.rightMenu.inc_all_connections = value


class EducationApp(App):
    def build(self):
        Builder.load_file('widgets.kv')
        return Education()


window_size = [window_height + menu_width, window_height]
Gas = gas.Neural_Gas()
Gas.max_neurons = max_neurons
Gas.winner_step = winner_step
Gas.neighbour_step = neighbour_step
Gas.init_neurons = init_neurons
Gas.max_age = max_connection_age
Gas.d_error = d_error
Gas.birth_step = birth_step
Gas.birth_error = birth_error

if (platform == 'macosx'):
    Window.size = [window_size[0] // 2, window_size[1] // 2]
else:
    Window.size = window_size
EducationApp().run()