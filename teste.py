import os


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def calculadora(a, b, op):
    return operacoes[op](a, b)


operacoes = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "/": lambda x, y: x / y,
    "*": lambda x, y: x * y,
}

while True:
    try:
        num1 = int(input("Primeiro número: "))
        num2 = int(input("Primeiro número: "))
        op = input("Operação: ")

        resultado = calculadora(num1, num2, op)
        print("\nResultado: ", resultado)

        break

    except KeyError:
        clear_console()
        print("\nInforme uma operação válida!!\n")
        continue
    except ValueError:
        clear_console()
        print("\nInforme um numero!!\n")
        continue
