import numpy
import streamlit
import pandas
from matplotlib import pyplot
from scipy.misc import derivative
from scipy.optimize import curve_fit


def render_required_antibiotic_concentration_range():
    streamlit.subheader("Requirement for Growth Heterogeneity Module")
    initial_value = "0.0001, 0.0093,0.0113,0.0136,0.0163,0.0197,0.0237,0.0286,0.0344,0.0415"
    ab_input = streamlit.text_input(
        "Since the range of antibiotic concentration is needed, gives the antibiotic concentration range with comma "
        "here:", initial_value
    )
    #ab_input = str(ab_input)[1:-1]
    streamlit.warning(
        "**IMPORTANT NOTE**: Write the antibiotic concentration separated with comma and put 0.0001 as a control. Put "
        "the list corresponds to the 'Labels' which has listed under your data above. Example: 0.0001, 0.0093,0.0113,"
        "0.0136,0.0163,0.0197,0.0237,0.0286,0.0344,0.0415"
    )
    streamlit.info("If there is no range of antibiotics in the required column, the results will not be generated.")
    return ab_input


def render_growth_heterogeneity_module(ab_input, second_dataframe, type_of_column):
    # This column is needed, otherwise,
    streamlit.write(second_dataframe)
    column1, column2 = streamlit.columns(2)
    data_frame_growth_heterogeneity = second_dataframe.copy()
    cek = second_dataframe['label'].squeeze()
    # streamlit.write(cek)
    data_frame_growth_heterogeneity['AB Concentration'] = pandas.Series(ab_input).str.split(
        ',',
        expand=True
    ).transpose()
    # st.subheader("Heteroresistance Module")
    data_frame_growth_heterogeneity['AB Concentration'] = pandas.to_numeric(
        data_frame_growth_heterogeneity['AB Concentration']
    )
    data_frame_growth_heterogeneity = data_frame_growth_heterogeneity.sort_values(by='AB Concentration', ascending=True)
    ctab_inv = numpy.array(data_frame_growth_heterogeneity['AB Concentration'])
    # ctan_inv=np.flip(ctab_inv)
    ctab = numpy.array(ctab_inv)
    for i in numpy.arange(ctab.size):
        # print i
        ctab[i] = ctab_inv[ctab_inv.size - i - 1]
    NDropletTab = numpy.array(data_frame_growth_heterogeneity["Total"])
    NDropletTab = numpy.flip(NDropletTab)
    NPosTab = numpy.array(data_frame_growth_heterogeneity['Positive'])
    NPosTab = numpy.flip(NPosTab)
    # st.write(data_frame_growth_heterogeneity)
    # st.write(ctab_inv)
    # st.write(NDropletTab)
    # st.write(NPosTab)
    fplus = numpy.array(NPosTab * 1.0 / NDropletTab)
    fplus.shape = (1, len(fplus))
    tabN = NDropletTab
    tabN.shape = (1, len(fplus[0, :]))
    err_fplus = numpy.array(numpy.sqrt(fplus * (1 - fplus) / tabN))
    for i, j in numpy.ndindex(fplus.shape):  # type: ignore
        if fplus[i, j] > 0.999999 or fplus[i, j] < 0.00001:  # which means it is one
            err_fplus[i, j] = 1.0 / tabN[i, j]
    av_NCFU = numpy.array(-numpy.log(1 - fplus[:, -1]))
    err_av_NCFU = numpy.array(numpy.sqrt(fplus[:, -1] / (tabN[:, -1] * (1.0 - fplus[:, -1]))))
    av_NCFU_pos = numpy.array(av_NCFU / (1 - numpy.exp(-av_NCFU)))
    fi = numpy.array(fplus)
    err_fi = numpy.array(fplus)
    for i in range(len(fi[:, 0])):
        fi[i, :] = fplus[i, :] / (1.0 - numpy.exp(-av_NCFU[i]))  # Formula [05.11.2018 (4.7)]
        err_fi[i, :] = numpy.sqrt(  # Formula [05.11.2018 (4B.4)]
            (err_fplus[i, :] / (1.0 - numpy.exp(-av_NCFU[i]))) ** 2
            + (fi[i, :] * err_av_NCFU[i] * numpy.exp(-av_NCFU[i]) / (1.0 - numpy.exp(-av_NCFU[i]))) ** 2
        )

    def gompertz(c, p1, p2):
        return numpy.exp(-(c / p1) ** numpy.abs(p2) * numpy.sign(p2))  # See ESI

    cMIC = numpy.array(av_NCFU)
    err_cMIC = numpy.array(av_NCFU)
    cMIC_50 = numpy.array(av_NCFU)
    err_cMIC_50 = numpy.array(av_NCFU)
    popt = [355., 1.]
    # Figure for gompertz_model
    # creating a dictionary
    font = {'size': 20}
    # using rc function
    pyplot.rc('font', **font)
    for i in range(len(fi[:, 0])):
        if i < 0:
            continue
        # Fit only those data where are numbers (omit nan - they may appear in fplus)
        wherenumbers = numpy.isfinite(fi[i, :])
        if not numpy.all(wherenumbers):
            print('concentration i, ctab[i]=', i, ctab[i], ' Some data are not numbers: wherenumbers=', wherenumbers)

        popt, pcov = curve_fit(
            gompertz,
            ctab[wherenumbers],
            fi[i, :][wherenumbers],
            sigma=err_fi[i, :][wherenumbers],
            absolute_sigma=True, p0=[av_NCFU[i], 0.1]
        )
        perr = numpy.sqrt(numpy.diag(pcov))  # Gives standard deviation of determined fitting parameters

        # Error of cMIC    [paper notes 05.11.2018 (5.10)]
        p1 = popt[0]
        p2 = popt[1]
        err_p1 = perr[0]
        err_p2 = perr[1]

        cMIC[i] = popt[0] * numpy.exp(1.0 / popt[1])  # See ESI
        err_cMIC[i] = numpy.sqrt(
            (cMIC[i] / p1 * err_p1) ** 2
            + (p1 / p2 ** 2 * cMIC[i] * err_p2) ** 2
        )
        # st.write('cMIC[i]:',cMIC[i],'+-',err_cMIC[i])

        cMIC_50[i] = p1 * numpy.log(2) ** (1.0 / p2)
        err_cMIC_50[i] = cMIC_50[i] * numpy.sqrt(
            (err_p1 / p1) ** 2 + (numpy.log(numpy.log(2.0)) * err_p2 / p2 ** 2) ** 2
        )

        # st.write('cMIC_50[i]:',cMIC_50[i],'+-',err_cMIC_50[i])
        # Find concentration index for which fi crosses 1/2
        ic05 = numpy.argmin((fi[i, wherenumbers][:-1] - 0.5) * (fi[i, wherenumbers][1:] - 0.5))
        # st.write('check:',fi[i,wherenumbers][ic05],fi[i,wherenumbers][ic05+1])
        err_cMIC_50[i] = min(err_cMIC_50[i], numpy.abs((ctab[wherenumbers][ic05] - ctab[wherenumbers][ic05 + 1]) / 2.0))
        # st.write('cMIC_50[i]:',cMIC_50[i],'+-',err_cMIC_50[i])

        if type_of_column == "Gompertz fitting":
            fig6 = pyplot.figure(figsize=(14, 6))
            pyplot.subplot(111)
            ctab_many = numpy.geomspace(ctab[0], ctab[-2] / 2, num=200)
            pyplot.plot(
                ctab_many, gompertz(ctab_many, popt[0], popt[1]), label='Gompertz  $p_1=' + str(round(p1, 3)) +
                                                                        ' \pm ' + str(round(err_p1, 3)) +
                                                                        ' \\ p_2= ' + str(
                    round(p2, 1)
                ) + '\pm ' + str(round(err_p2, 2)) + ' $'
                , color='k'
            )
            pyplot.errorbar(
                ctab[wherenumbers][:-1],
                fi[i, :][wherenumbers][:-1],
                yerr=err_fi[i, :][wherenumbers][:-1],
                ls='none',
                label='$\langle N_{CFU} \\rangle =' + str(round(av_NCFU[i], 4)) + '$',
                color='k'
            )
            pyplot.plot(
                ctab[wherenumbers][:-1],
                fi[i, :][wherenumbers][:-1],
                color='lime',
                marker='.',
                ls='none'
            )
            pyplot.legend(frameon=False, loc=1, fontsize=11)
            pyplot.ylabel('viability,  $f_+(c)/f_+(0)$', rotation=90, fontsize=12, labelpad=10)
            pyplot.xlabel('$c \\ [\mu g/ ml] $', rotation=0, fontsize=12)
            # plt.xlim(0.01,0.04)
            # plt.ylim(ymin=-0.02,ymax=1.2)
            # _set_plot_axis_labels(fig6, '$c \\ [\mu g/ ml] $', 'viability,  $f_+(c)/f_+(0)$', column2, column2, "ghx", "ghy")
            column1.pyplot(fig6)

        if type_of_column == "Single cell viability and MIC probability density":
            # st.subheader("Single Cell Viability")

            def partial_derivative(func, dx, n=1, var=0, order=7, point=None):
                if point is None:
                    point = []
                args = point[:]

                def wraps(x):
                    args[var] = x
                    return func(*args)

                return derivative(wraps, point[var], dx=dx, n=n, order=order)

            def gompertz(c, p1, p2):
                return numpy.exp(-(c / p1) ** numpy.abs(p2) * numpy.sign(p2))  # See ESI

            cMIC = numpy.array(av_NCFU)
            err_cMIC = numpy.array(av_NCFU)
            cMIC_50 = numpy.array(av_NCFU)
            err_cMIC_50 = numpy.array(av_NCFU)
            popt = [355., 1.]

            def fit_fun(c, cscale, alpha, a1):
                return 1 / (1 + (c / cscale) ** alpha + a1 * (c / cscale) ** (2 * alpha))

            i = 0
            wherenumbers = numpy.isfinite(fi[i, :])
            if not numpy.all(wherenumbers):
                streamlit.write(
                    'concentration i, ctab[i]=', i, ctab[i], ' Some data are not numbers: wherenumbers=',
                    wherenumbers
                )
            popt, pcov = curve_fit(
                fit_fun, ctab[wherenumbers], fi[i, :][wherenumbers],
                sigma=err_fi[i, :][wherenumbers],
                absolute_sigma=True
            )
            perr = numpy.sqrt(numpy.diag(pcov))  # Gives standard deviation of the parameters
            # st.write('popt:',popt)
            # st.write('perr:',perr)

            popt_article = popt
            perr_article = perr

            def err_fit_fun(fit_fun, c, *args):
                if numpy.isscalar(c):
                    carr = numpy.array([c])
                else:
                    carr = numpy.array(c)
                dx = 1.e-3
                n = 1
                order = 7
                popt = numpy.array(args[:len(args) // 2])
                perr = numpy.array(args[len(args) // 2:])
                res = numpy.array(carr)  # create array of same length
                for j in range(len(carr)):
                    point = numpy.concatenate((numpy.array([carr[j]]), popt), axis=0)
                    s2 = 0
                    for i in range(len(popt)):
                        s2 = s2 + (partial_derivative(fit_fun, dx=dx, n=1, var=(i + 1), point=point[:], order=7) * perr[
                            i]) ** 2
                    res[j] = numpy.sqrt(s2)
                return res

            fig7 = pyplot.figure(figsize=(14, 6))
            ve = numpy.concatenate((popt, perr), axis=0)
            ctab_many = numpy.geomspace(ctab[0], ctab[-1], num=200)
            pyplot.plot(
                ctab_many,
                fit_fun(ctab_many, *popt),
                color='k',
                ls='-',
                label='$1/[1+(c/c_s)^\\alpha + a_1 (c/c_s)^{2\\alpha}]$'
            )
            pyplot.fill_between(
                ctab_many,
                fit_fun(ctab_many, *popt) - err_fit_fun(fit_fun, ctab_many, *ve),
                fit_fun(ctab_many, *popt) + err_fit_fun(fit_fun, ctab_many, *ve),
                facecolor='#119da4',
                alpha=0.1
            )
            pyplot.plot(
                ctab,
                fi[0, :],
                label='repeated (dense) exp, $\langle N_{CFU} \\rangle$ = ' + str(round(av_NCFU[i], 2)),
                color='lime',
                marker='.',
                ls='none',
                markersize=6
            )
            pyplot.errorbar(ctab, fi[0, :], yerr=err_fi[0, :], ls='none')
            pyplot.xlabel('$c \\ [\mu g/ ml] $', rotation=0, fontsize=12)
            pyplot.legend(frameon=False, loc=1, fontsize=11)
            pyplot.ylabel('$f_+(c)/f_+(0)$', rotation=90, fontsize=12, labelpad=10)
            column1.pyplot(fig7)

            # Probability for AB concentration among droplets
            # st.subheader("MIC Probability Density")
            # st.warning("*The single cell viability needs to be performed first.")

            # def prob_fit_fun(c, cscale, alpha, a1, a2):
            #     dx = 1.e-3
            #     n = 1
            #     order = 7
            #     return -partial_derivative(fit_fun, dx=dx, n=1, var=0, point=[c, cscale, alpha, a1, a2], order=7)

            def prob_fit_fun(c, cscale, alpha, a1):
                dx = 1.e-3
                n = 1
                order = 7
                return -partial_derivative(fit_fun, dx=dx, n=n, var=0, point=[c, cscale, alpha, a1], order=order)

            fig8 = pyplot.figure(figsize=(14, 6))
            ctab_many = numpy.geomspace(ctab[0], ctab[-1], num=400)
            pyplot.plot(
                ctab_many, prob_fit_fun(ctab_many, *popt), color='k', ls='-',
                label='$ p^{fit}(c)$'
            )
            pyplot.fill_between(
                ctab_many,
                prob_fit_fun(ctab_many, *popt) - err_fit_fun(prob_fit_fun, ctab_many, *ve),
                prob_fit_fun(ctab_many, *popt) + err_fit_fun(prob_fit_fun, ctab_many, *ve),
                facecolor='#119da4',
                alpha=0.05
            )

            pyplot.legend(frameon=False, loc=1, fontsize=11)
            pyplot.ylabel('$p(c) \\ [ml/\mu g]$', rotation=90, fontsize=12, labelpad=10)
            pyplot.xlabel('$c \\ [\mu g/ ml] $', rotation=0, fontsize=12)
            # plt.xlim(0,0.7)
            column2.pyplot(fig8)