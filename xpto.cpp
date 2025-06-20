#include <iostream>
#include <vector>
#include <iomanip>

double interpolacao_lagrange(const std::vector<double> &valores_x, const std::vector<double> &valores_f_x, double x_interpolar)
{
    int n_pontos = valores_x.size();
    double resultado_polinomio = 0.0;

    std::cout << "\n+------------------------ TABELA DE CÁLCULO ------------------------+" << std::endl;
    std::cout << "|  k  |   x[k]   |  f(x[k])  |     Lk(x)     | f(x[k])*Lk(x) |  Soma Parcial  |" << std::endl;
    std::cout << "+-----+----------+-----------+---------------+----------------+----------------+" << std::endl;

    for (int k = 0; k < n_pontos; ++k)
    {
        double L_k = 1.0;
        for (int j = 0; j < n_pontos; ++j)
            if (j != k)
                L_k *= (x_interpolar - valores_x[j]) / (valores_x[k] - valores_x[j]);

        double termo_completo = valores_f_x[k] * L_k;
        resultado_polinomio += termo_completo;

        std::cout << std::setw(5) << k
                  << " | " << std::setw(8) << valores_x[k]
                  << " | " << std::setw(9) << valores_f_x[k]
                  << " | " << std::setw(13) << L_k
                  << " | " << std::setw(14) << termo_completo
                  << " | " << std::setw(14) << resultado_polinomio << " |" << std::endl;
    }

    std::cout << "+------------------------------------------------------------------+\n"
              << std::endl;
    return resultado_polinomio;
}

int main()
{
    std::cout << std::fixed << std::setprecision(10);

    int quantidade_pontos;
    std::cout << "Digite a quantidade de pontos: ";
    std::cin >> quantidade_pontos;

    std::vector<double> valores_x(quantidade_pontos);
    std::vector<double> valores_f_x(quantidade_pontos);

    for (int i = 0; i < quantidade_pontos; ++i)
    {
        std::cout << "x[" << i << "]: ";
        std::cin >> valores_x[i];
        std::cout << "f(x)[" << i << "]: ";
        std::cin >> valores_f_x[i];
    }

    double x_para_estimar;
    std::cout << "Digite o valor de x para estimar f(x): ";
    std::cin >> x_para_estimar;

    double f_x_estimado = interpolacao_lagrange(valores_x, valores_f_x, x_para_estimar);
    std::cout << ">>> f(" << x_para_estimar << ") ≈ " << f_x_estimado << std::endl;

    return 0;
}