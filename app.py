from flask import Flask, request, render_template
from sympy import Matrix, Rational, latex
import json

app = Flask(__name__)


def parse_element(elem):
    if '/' in elem:
        num, den = elem.split('/', 1)
        return Rational(num, den)
    try:
        return int(elem)
    except:
        return Rational(elem)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            m = int(request.form['rows'])
            n = int(request.form['cols'])
            matrix = []
            errors = []

            # 验证行数和列数是否为正整数
            if m <= 0 or n <= 0:
                return render_template('index.html', error="行数和列数必须为正整数！")

            for i in range(m):
                row = []
                for j in range(n):
                    elem = request.form.get(f'matrix[{i}][{j}]', '0').strip()
                    try:
                        row.append(parse_element(elem))
                    except Exception as e:
                        errors.append(f"行{i + 1}列{j + 1}: 无效输入 '{elem}'")
                matrix.append(row)

            if errors:
                return render_template('index.html', error="<br>".join(errors))

            mat = Matrix(matrix)
            results = {}

            # 计算各项结果
            results['rank'] = mat.rank()
            results['is_square'] = mat.is_square
            if mat.is_square:
                # 直接将行列式转换为 LaTeX 格式
                results['det'] = latex(mat.det())
                results['charpoly'] = latex(mat.charpoly().as_expr())
                try:
                    eigen = mat.eigenvects()
                    results['eigen'] = [
                        {
                            'value': latex(val.evalf(4)),
                            'multiplicity': mult,
                            'vectors': [latex(vec.normalized()) for vec in vectors]
                        } for val, mult, vectors in eigen
                    ]
                except Exception as e:
                    results['eigen_error'] = str(e)

                # 计算矩阵的逆
                try:
                    inv = mat.inv()
                    results['inv'] = latex(inv)
                except Exception as e:
                    results['inv_error'] = str(e)

                # 谱分解（假设矩阵可对角化）
                try:
                    P, D = mat.diagonalize()
                    results['spectral_P'] = latex(P)
                    results['spectral_D'] = latex(D)
                except Exception as e:
                    results['spectral_error'] = str(e)

                # LU 分解
                try:
                    L, U, _ = mat.LUdecomposition()
                    results['LU_L'] = latex(L)
                    results['LU_U'] = latex(U)
                except Exception as e:
                    results['LU_error'] = str(e)
            else:
                results['det'] = None
                results['inv'] = None
                results['spectral_P'] = None
                results['spectral_D'] = None
                results['LU_L'] = None
                results['LU_U'] = None

            # 计算 RREF 并转为 LaTeX
            rref = mat.rref()[0]
            results['rref'] = latex(rref)
            results['original'] = latex(mat)

            return render_template('index.html', results=results)

        except Exception as e:
            return render_template('index.html', error=f"系统错误: {str(e)}")

    return render_template('index.html')
#on

if __name__ == '__main__':
    app.run(debug=True)