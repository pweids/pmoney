import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

class Plotter():

    def __init__(self, budget):
        self.budget = budget

    def build_bars_and_save_image(self, dir):
        self.build_bar_graph()
        return self.save_image(dir)

    def build_bar_graph(self):
        variable = self.budget.variable_costs.calculate_amount_by_category()
        variable = {k: -v for k, v in variable.items()}

        fig, ax = plt.subplots(1, 1, figsize=(12,4))
        plt.bar(range(len(variable)), variable.values(), align="center")
        tick = mtick.StrMethodFormatter('${x:,.0f}')
        ax.yaxis.set_major_formatter(tick)
        plt.xticks(range(len(variable)), list(variable.keys()))

    def save_image(self, dir):
        name = "{}/{}-{}.png".format(dir, self.budget.month, self.budget.year)
        plt.savefig(name, bbox_inches='tight')
        
