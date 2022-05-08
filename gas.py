import random

# не является честью api, только читайте поля этого класса
class Connection():
    def __init__(self, neuron1, neuron2) -> None:
        self.neuron1 = neuron1
        self.neuron2 = neuron2
        self.age = 0
    
    def another_neuron(self, neuron):
        if neuron is self.neuron1:
            return self.neuron2
        if neuron is self.neuron2:
            return self.neuron1
        return None

# не является честью api, только читайте поля этого класса
class Neuron():
    def __init__(self, pos) -> None:
        # положение нейрона среди данных
        # размерность определяется автоматически в начале обучения
        self.pos = pos
        # связи с другими нейронами
        # каждая связь хранится в обоих нейронах, а также в самом газе
        self.connections = []
        # нейрон накапливает ошибку моделирования данных (сумма расстояний от нейрона до данных)
        # для которых этот нейрон является близжайшим
        # d цикле она умножается на число < 1, чтобы не получалось слишком большое значение ошибки
        self.error = 0        
        # dynamic value
        # дистанция до точки, нужна для выбора близжайшего нейрона
        self.distanse = 0
        # helps divide by classes
        self.sorted = False

    def __str__(self) -> str:
        return 'Neuron at ' + str(self.pos)

    def have_connections(self):
        return len(self.connections) != 0
    
    def add_connection(self, connection):
        if connection not in self.connections:
            self.connections.append(connection)
    
    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)
    
    def get_distanse(self, point):
        d = 0
        for i in range(len(point)):
            d += (point[i] - self.pos[i]) ** 2
        return d ** 0.5
    
    def move(self, rate, point):
        for i in range(len(self.pos)):
            dx = point[i] - self.pos[i]
            self.pos[i] += dx * rate

    def increase_ages(self):
        for connection in self.connections:
            connection.age += 1

    def reset2zeroConnectin(self, neuron):
        for conn in self.connections:
            if (conn.neuron1, conn.neuron2) == (self, neuron) or \
                (conn.neuron2, conn.neuron1) == (self, neuron):
                conn.age = 0
                return None
        conn = Connection(self, neuron)
        self.add_connection(conn)
        neuron.add_connection(conn)
        return conn

    def find_neuron_with_largest_error(self):
        connection = self.connections[0]
        largest = connection.neuron1
        if largest == self:
            largest = connection.neuron2
        for conn in self.connections:
            neuron = conn.neuron1
            if neuron is self:
                neuron = conn.neuron2
            if neuron.error > largest.error:
                largest = neuron
                connection = conn
        return largest, connection


class Neural_Gas():
    """
    можете менять все свойства этого класса снаружи,
    кроме neurons, connections, step
    все дробные числа должны быть в промежутке от 0 до 1 включительно
    на целочисленные параметры ограничения даны в описании к свойствам
    методы апи класса помечены комментарием #api
    остальные методы для внутреннего пользования
    """

    def __init__(self) -> None:
        # список связей всех нейронов
        self.connections = []
        # список нейронов
        # заполняется при обучении
        self.neurons = []

        # это - доля от отрезка между точкой и нейроном, как 
        # следует сдвигать нейрон близжайший и второй победитель
        self.winner_step = .05
        self.neighbour_step = 0.005
        # начальное кол-во нейронов
        # >= 2
        self.init_neurons = 2
        # максимальный возраст связи, после которого связь уничтожается
        # нейрон без связей уничтожается
        # > 0
        self.max_age = 100
        # максимум нейронов модели (достигается обычно в хорошей модели)
        # >= 2
        self.max_neurons = 100
        # во сколько раз уменьшать накопленную ошибку нейронов за раз
        self.d_error = 0.95
        # как часто создавать новые нейроны, если это возможно
        # 1 итерация - 1 акт обучения на 1 точке
        # birth_step измеряется в итерациях и должен быто целым > 0
        self.birth_step = 30
        # при рождении нейрона ошибка его новых соседей домножается на это число
        # по идее, должен быть меньше, чем d_error
        self.birth_error = 0.5
        # увеличивать возраст связей у всех или только связей от нейрона победителя
        # False - соседей, работает стабильнее
        self.increment_all = False
        # number of iteration when educate
        # счётчик для внутреннего пользования
        self.step = 0
    
    # создаёт новый нейрон между худшим нейроном и его самим плохим соседом
    # рвёт всязь между ними и сановится посередине, создавая 2 связи
    # плохой нейрон - с max накопленной ошибкой
    # 2 этих нейрона уменьшают ошибку в birth_error раз, новичок перед этим 
    # получает среднее от их ошибок
    def create_neuron(self):
        largest = max(self.neurons, key=lambda neuron: neuron.error)
        second, connection = largest.find_neuron_with_largest_error()

        pos = []
        for i in range(len(second.pos)):
            pos.append((largest.pos[i] + second.pos[i])/2)
        new = Neuron(pos = pos)
        self.neurons.append(new)

        largest.remove_connection(connection)
        second.remove_connection(connection)
        self.connections.remove(connection)

        connection = Connection(new, largest)
        new.add_connection(connection)
        largest.add_connection(connection)
        self.connections.append(connection)

        connection = Connection(new, second)
        new.add_connection(connection)
        second.add_connection(connection)
        self.connections.append(connection)

        second.error *= self.birth_error
        largest.error *= self.birth_error
        new.error = (second.error + largest.error) / 2

    # сдвигает 2 близжайших нейрона в направлении этой точки у 
    # увеличивает ошибку, обноляет возраст связи, создаёт её, если не было
    def move_2_neurons(self, point, increment_all):
        for neuron in self.neurons:
            neuron.distanse = neuron.get_distanse(point)

        smallest = self.neurons[0]
        second = self.neurons[1]
        for neuron in self.neurons:
            if neuron.distanse < smallest.distanse:
                second = smallest
                smallest = neuron
            elif neuron.distanse < second.distanse:
                second = neuron

        smallest.error += smallest.distanse ** 2
        smallest.move(self.winner_step, point)
        second.move(self.neighbour_step,point)

        if increment_all:
            for conn in self.connections:
                conn.age += 1
        else:
            smallest.increase_ages()
        res = smallest.reset2zeroConnectin(second)
        if res != None:
            self.connections.append(res)

    # проводит полный акт обучения для 1 точки
    def educate_for_one_point(self, point):
        self.step += 1
        self.move_2_neurons(point, self.increment_all)

        conns = []
        for conn in self.connections:
            if conn.age > self.max_age:
                conn.neuron1.remove_connection(conn)
                conn.neuron2.remove_connection(conn)
            else:
                conns.append(conn)
        self.connections = conns

        neurons = []
        for neuron in self.neurons:
            if neuron.have_connections():
                neurons.append(neuron)
        self.neurons = neurons
    
        if self.step % self.birth_step == 0 and len(self.neurons) < self.max_neurons:
            self.create_neuron()
        
        for neuron in self.neurons:
            neuron.error *= self.d_error

    # api
    # обучает на данных, проходя по ним epochs раз в разном порядке
    # печать прогресса в терминал - interactive = True
    def educate(self, data_, epochs = 20, interactive = False, increment_all = False):
        if self.init_neurons < 2:
            raise Exception('Neural_Gas.init_neurons must be >= 2')

        data = data_.copy()

        # initial values
        self.increment_all = increment_all
        for i in range(self.init_neurons):
            self.neurons.append(Neuron(pos = list(random.choice(data))))
        for i in range(self.init_neurons):
            for y in range(i+1,self.init_neurons):
                connection = Connection(self.neurons[i], self.neurons[y])
                self.neurons[i].add_connection(connection)
                self.neurons[y].add_connection(connection)
                self.connections.append(connection)

        # educate
        for ep in range(epochs):
            if interactive:
                print(f'epoch № {ep+1} / {epochs}')
            random.shuffle(data)
            for point in data:
                self.educate_for_one_point(point)
    
    # api
    # эквивалентен методу educate
    # возвращает итератор обучения, который прерывается каждые iteration_step итераций
    # можно использовать для рисования интерфейса приложения, ка в примере, или для лююбых других целей
    # выбрасывает исключение в конце обучения, как и обычный итератор в python
    def education_iterator(self, data_, epochs = 20, interactive = False, itetation_step = 0, increment_all = False):
        if self.init_neurons < 2:
            raise Exception('Neural_Gas.init_neurons must be >= 2')

        data = data_.copy()

        # initial values
        self.increment_all = increment_all
        for i in range(self.init_neurons):
            self.neurons.append(Neuron(pos = list(random.choice(data))))
        for i in range(self.init_neurons):
            for y in range(i+1,self.init_neurons):
                connection = Connection(self.neurons[i], self.neurons[y])
                self.neurons[i].add_connection(connection)
                self.neurons[y].add_connection(connection)
                self.connections.append(connection)
        
        # educate
        for ep in range(epochs):
            if interactive:
                print(f'epoch № {ep+1} / {epochs}')
            random.shuffle(data)
            for point in data:
                self.educate_for_one_point(point)
                if self.step % itetation_step == 0:
                    yield ep, self.step

    # api
    # сбрасывает прогресс обучеиния (НО НЕ ПАРАМЕТРЫ)
    # НЕ ВЫЗЫВАЙТЕ ВО ВРЕМЯ ОБУЧЕНИЯ !!!!!
    def reset_state(self):
        self.neurons = []
        self.connections = []
        self.step = 0

    # api
    # после обучения можно разделить все нейроны на кластеры
    # если нейроны разделились на несколько несоединённых областей
    # возвращает список групп (1 группа - список из нейронов, в неё входящих)
    def divide_by_classes(self):
        classes = []
        cur_class = []
        stack = []
        i = 0
        n = len(self.neurons)
        for neuron in self.neurons:
            neuron.sorted = False
        
        while i < n:
            cur_class.append(self.neurons[i])
            self.neurons[i].sorted = True
            for conn in self.neurons[i].connections:
                neu2 = conn.another_neuron(self.neurons[i])
                if not neu2.sorted:
                    stack.append(neu2)
            
            while stack != []:
                neu = stack.pop()
                neu.sorted = True
                cur_class.append(neu)
                for conn in neu.connections:
                    neu2 = conn.another_neuron(neu)
                    if not neu2.sorted:
                        if not neu2 in stack:
                            stack.append(neu2)
                
            classes.append(cur_class)
            cur_class = []
            stack = []
            i += 1
            while i < n and self.neurons[i].sorted:
                i += 1

        return classes

# tests
if __name__ == '__main__':
    gas = Neural_Gas()

    neuron1 = Neuron([10, 10])
    neuron2 = Neuron([20,20])
    neuron3 = Neuron([30,30])
    neuron4 = Neuron ([40,40])
    neuron5 = Neuron([50,50])

    conn1 = Connection(neuron1, neuron2)
    conn2 = Connection(neuron3, neuron2)
    # conn3 = Connection(neuron3, neuron4)
    conn4 = Connection(neuron4, neuron5)

    for conn in [conn1, conn2, conn4]:
        gas.connections.append(conn)
    # gas.connections.append(conn3)

    for neuron in [neuron1, neuron2, neuron3, neuron4, neuron5]:
        gas.neurons.append(neuron)
    neuron1.add_connection(conn1)
    neuron2.add_connection(conn1)
    neuron2.add_connection(conn2)
    neuron3.add_connection(conn2)
    #neuron3.add_connection(conn3)
    #neuron4.add_connection(conn3)
    neuron4.add_connection(conn4)
    neuron5.add_connection(conn4)

    for cl in gas.divide_by_classes():
        print('class')
        for el in cl:
            print(el.__str__())


