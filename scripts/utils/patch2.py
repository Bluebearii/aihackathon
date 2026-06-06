import sys

with open('dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add to pages list in sidebar if it's not there
if '"🚫 No-Show Analysis"' not in content:
    content = content.replace('"📋 Data Tables",', '"📋 Data Tables",\n        "🚫 No-Show Analysis",')

# Append the No-Show Analysis page to the end
new_page = """
# ============================================================
# PAGE 9: NO-SHOW ANALYSIS
# ============================================================

elif page == "🚫 No-Show Analysis":
    st.markdown('''
    <div class="main-header">
        <h1>🚫 Medical Appointments No-Show Analysis</h1>
        <p>Exploring the business and operational impact of missed appointments</p>
    </div>
    ''', unsafe_allow_html=True)

    @st.cache_data(ttl=3600, show_spinner="Loading No-Show Data...")
    def load_noshow_data():
        df_ns = pd.read_csv('data_source/medical-appointments-no-show-en.csv')
        df_ns['appointment_date'] = pd.to_datetime(df_ns['appointment_date'], format='%d/%m/%Y', errors='coerce')
        df_ns['no_show_binary'] = (df_ns['no_show'] == 'yes').astype(int)
        df_ns.drop_duplicates(inplace=True)
        return df_ns

    try:
        df_ns = load_noshow_data()
        
        # Top KPIs
        total_appt = len(df_ns)
        total_noshow = df_ns['no_show_binary'].sum()
        noshow_rate = total_noshow / total_appt * 100 if total_appt > 0 else 0
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(kpi_card("Total Appointments", f"{total_appt:,}", "", "#2A9D8F"), unsafe_allow_html=True)
        with c2:
            st.markdown(kpi_card("Total No-Shows", f"{total_noshow:,}", "", "#E76F51"), unsafe_allow_html=True)
        with c3:
            st.markdown(kpi_card("No-Show Rate", f"{noshow_rate:.1f}%", "", "#E9C46A"), unsafe_allow_html=True)
            
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 1. No-Show Pie Chart
            ns_counts = df_ns['no_show'].value_counts()
            fig1 = px.pie(values=ns_counts.values, names=ns_counts.index, 
                         color_discrete_sequence=[COLORS['teal'], COLORS['coral']], hole=0.4)
            fig1.update_layout(**chart_layout("Showed Up vs No-Show", height=400))
            st.plotly_chart(fig1, use_container_width=True)
            
            st.markdown(analysis_box(
                "Distribution of patients who showed up versus those who missed their appointments.",
                problem="A high no-show rate represents wasted provider time, lost revenue, and delayed care."
            ), unsafe_allow_html=True)
            
        with col2:
            # 2. No-Show by Gender
            gender_ns = df_ns.groupby('gender')['no_show_binary'].mean().reset_index()
            gender_ns['no_show_rate'] = gender_ns['no_show_binary'] * 100
            fig2 = px.bar(gender_ns, x='gender', y='no_show_rate', color='gender',
                          color_discrete_sequence=[COLORS['blue'], COLORS['coral']],
                          labels={'gender': 'Gender', 'no_show_rate': 'No-Show Rate (%)'})
            fig2.update_layout(**chart_layout("No-Show Rate by Gender", height=400))
            st.plotly_chart(fig2, use_container_width=True)
            
            st.markdown(analysis_box(
                "Comparison of no-show rates between Male and Female patients.",
                "Identify demographic trends to tailor communication and reminder strategies."
            ), unsafe_allow_html=True)
            
        st.markdown("---")
        
        col3, col4 = st.columns(2)
        
        with col3:
            # 3. No-Show by Specialty
            spec_counts = df_ns['specialty'].value_counts()
            top_specs = spec_counts.head(10).index
            spec_ns = df_ns[df_ns['specialty'].isin(top_specs)].groupby('specialty')['no_show_binary'].mean().reset_index()
            spec_ns['no_show_rate'] = spec_ns['no_show_binary'] * 100
            spec_ns = spec_ns.sort_values('no_show_rate', ascending=True)
            
            fig3 = px.bar(spec_ns, x='no_show_rate', y='specialty', orientation='h',
                          color='no_show_rate', color_continuous_scale='Reds',
                          labels={'specialty': 'Specialty', 'no_show_rate': 'No-Show Rate (%)'})
            fig3.update_layout(**chart_layout("No-Show Rate by Top 10 Specialties", height=400), coloraxis_showscale=False)
            st.plotly_chart(fig3, use_container_width=True)
            
            st.markdown(analysis_box(
                "No-show rate across the most commonly visited specialties.",
                problem="Certain specialties may experience higher no-shows due to the nature of care (e.g., preventative vs urgent)."
            ), unsafe_allow_html=True)
            
        with col4:
            # 4. Age Distribution of No-Shows
            df_ns_age = df_ns.dropna(subset=['age'])
            df_ns_age = df_ns_age[df_ns_age['age'] < 100] 
            
            fig4 = px.histogram(df_ns_age, x='age', color='no_show', barmode='overlay',
                                color_discrete_sequence=[COLORS['teal'], COLORS['coral']],
                                opacity=0.7, nbins=30)
            fig4.update_layout(**chart_layout("Age Distribution: Show vs No-Show", height=400))
            st.plotly_chart(fig4, use_container_width=True)
            
            st.markdown(analysis_box(
                "Age demographic breakdown showing the volume of missed appointments across different age groups."
            ), unsafe_allow_html=True)
            
        st.markdown("---")
        
        # 5. No-Show Reasons
        st.markdown('<div class="section-header">🤔 Why do patients miss appointments?</div>', unsafe_allow_html=True)
        
        def categorize_reason(reason):
            if pd.isna(reason): return np.nan
            r = str(reason).lower().strip()
            if any(w in r for w in ['doente', 'doença', 'gripe', 'gripado', 'febre', 'virose', 'tosse', 'diarreia', 'vômito', 'dor de', 'passou mal', 'sintoma']): return 'Illness'
            if any(w in r for w in ['covid', 'quarentena', 'isolamento', 'vacina']): return 'COVID / Vaccine'
            if any(w in r for w in ['transporte', 'carro', 'moto', 'ônibus', 'trânsito']): return 'Transportation'
            if any(w in r for w in ['desmarcado', 'cancelad', 'remarcado', 'reagendado']): return 'Cancelled / Rescheduled'
            if any(w in r for w in ['cirurgia', 'internado', 'exame', 'médico', 'dentista']): return 'Other Medical'
            if any(w in r for w in ['mãe', 'pai', 'filha', 'falecimento', 'morte', 'familiar']): return 'Family Issue'
            if any(w in r for w in ['trabalho', 'escola', 'aula', 'curso']): return 'Work / School'
            if any(w in r for w in ['chuva', 'frio', 'mau tempo']): return 'Weather'
            if any(w in r for w in ['desist', 'mudou']): return 'Dropped Out / Moved'
            if any(w in r for w in ['viaj', 'viagem']): return 'Traveling'
            if any(w in r for w in ['caiu', 'acidente', 'machucou', 'fraturou']): return 'Accident / Injury'
            return 'Other'

        if 'no_show_reason' in df_ns.columns:
            df_ns['no_show_reason_category'] = df_ns['no_show_reason'].apply(categorize_reason)
            cats = df_ns[df_ns['no_show'] == 'yes']['no_show_reason_category'].dropna().value_counts()
            
            if len(cats) > 0:
                fig5 = px.bar(x=cats.values, y=cats.index, orientation='h',
                              color=cats.values, color_continuous_scale='Reds',
                              labels={'x': 'Count', 'y': 'Reason Category'})
                fig5.update_layout(**chart_layout("No-Show Reasons by Category", height=450, yaxis={'categoryorder': 'total ascending'}), coloraxis_showscale=False)
                st.plotly_chart(fig5, use_container_width=True)
                st.markdown(analysis_box("Categorized reasons provided by patients for missing their appointments.", problem="Many cancellations are due to illness or transportation issues, which could be mitigated by offering telehealth options."), unsafe_allow_html=True)
                st.markdown("---")
        
        col5, col6 = st.columns(2)
        with col5:
            # 6. No-Show by Month
            if 'appointment_month' in df_ns.columns:
                month_order = ['jan', 'feb', 'mar', 'apr', 'may', 'june', 'july', 'aug', 'sept', 'oct', 'nov', 'dec']
                month_ns = df_ns.groupby('appointment_month')['no_show_binary'].mean().reset_index()
                month_ns['rate'] = month_ns['no_show_binary'] * 100
                month_ns['appointment_month'] = pd.Categorical(month_ns['appointment_month'], categories=month_order, ordered=True)
                month_ns = month_ns.sort_values('appointment_month').dropna()
                
                fig6 = px.line(month_ns, x='appointment_month', y='rate', markers=True,
                               labels={'appointment_month': 'Month', 'rate': 'No-Show Rate (%)'})
                fig6.update_layout(**chart_layout("No-Show Rate by Month", height=400))
                st.plotly_chart(fig6, use_container_width=True)
                st.markdown(analysis_box("Trend of no-show rates across different months."), unsafe_allow_html=True)

        with col6:
            # 7. No-Show by Shift
            if 'appointment_shift' in df_ns.columns:
                shift_ns = df_ns.groupby('appointment_shift')['no_show_binary'].mean().reset_index()
                shift_ns['rate'] = shift_ns['no_show_binary'] * 100
                fig7 = px.bar(shift_ns, x='appointment_shift', y='rate', color='appointment_shift',
                              color_discrete_sequence=[COLORS['amber'], COLORS['navy']],
                              labels={'appointment_shift': 'Shift', 'rate': 'No-Show Rate (%)'})
                fig7.update_layout(**chart_layout("No-Show Rate: Morning vs Afternoon", height=400), showlegend=False)
                st.plotly_chart(fig7, use_container_width=True)
                st.markdown(analysis_box("Comparison of missed appointments between morning and afternoon shifts."), unsafe_allow_html=True)

        st.markdown("---")
        
        col7, col8 = st.columns(2)
        with col7:
            # 8. Weather impact (Rain)
            if 'rain_intensity' in df_ns.columns:
                rain_ns = df_ns.groupby('rain_intensity')['no_show_binary'].mean().reset_index()
                rain_ns['rate'] = rain_ns['no_show_binary'] * 100
                fig8 = px.bar(rain_ns, x='rain_intensity', y='rate', color='rain_intensity',
                              color_discrete_sequence=[COLORS['amber'], COLORS['green'], COLORS['navy'], COLORS['teal']],
                              labels={'rain_intensity': 'Rain Intensity', 'rate': 'No-Show Rate (%)'})
                fig8.update_layout(**chart_layout("No-Show Rate by Rain Intensity", height=400), showlegend=False)
                st.plotly_chart(fig8, use_container_width=True)
                st.markdown(analysis_box("Impact of rain intensity on patient attendance."), unsafe_allow_html=True)

        with col8:
            # 9. Estimated Business Loss
            if 'specialty' in df_ns.columns:
                cost_estimates = {
                    'physiotherapy': 75, 'psychotherapy': 120, 'speech therapy': 100,
                    'occupational therapy': 90, 'enf': 60, 'psychology': 120,
                    'social service': 50, 'nutrition': 70
                }
                ns_only = df_ns[df_ns['no_show'] == 'yes'].copy()
                ns_only['est_cost'] = ns_only['specialty'].str.lower().map(cost_estimates).fillna(80)
                total_loss = ns_only['est_cost'].sum()
                loss_spec = ns_only.groupby('specialty')['est_cost'].sum().reset_index().sort_values('est_cost', ascending=False).head(10)
                
                fig9 = px.bar(loss_spec, x='est_cost', y='specialty', orientation='h',
                              color='est_cost', color_continuous_scale='Reds',
                              labels={'est_cost': 'Total Loss ($)', 'specialty': 'Specialty'})
                fig9.update_layout(**chart_layout(f"Estimated Revenue Loss (Total: ${total_loss:,.0f})", height=400, yaxis={'categoryorder': 'total ascending'}), coloraxis_showscale=False)
                st.plotly_chart(fig9, use_container_width=True)
                st.markdown(analysis_box("Estimated financial impact of missed appointments by specialty, assuming an average consultation cost per specialty.", problem="Significant revenue is lost due to empty slots that could have been filled by other patients."), unsafe_allow_html=True)

        st.markdown("---")
        
        # 10. Correlation Matrix
        st.markdown('<div class="section-header">🔗 Factors Correlated with No-Shows</div>', unsafe_allow_html=True)
        numeric_cols = ['no_show_binary', 'age', 'under_12_years_old', 'over_60_years_old',
                        'patient_needs_companion', 'average_temp_day', 'average_rain_day',
                        'max_temp_day', 'max_rain_day', 'rainy_day_before', 'storm_day_before']
        
        # Only keep columns that exist in df_ns
        numeric_cols = [c for c in numeric_cols if c in df_ns.columns]
        
        if len(numeric_cols) > 1:
            corr = df_ns[numeric_cols].corr().round(2)
            fig10 = ff.create_annotated_heatmap(
                z=corr.values, x=numeric_cols, y=numeric_cols,
                colorscale='RdBu_r', showscale=True, reversescale=False)
            fig10.update_layout(**chart_layout("Correlation Matrix", height=600))
            st.plotly_chart(fig10, use_container_width=True)
            st.markdown(analysis_box("Correlation heatmap between numerical variables and the likelihood of a no-show."), unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Could not load No-Show dataset: {e}")
"""

if '# PAGE 9: NO-SHOW ANALYSIS' not in content:
    with open('dashboard.py', 'w', encoding='utf-8') as f:
        f.write(content + "\n" + new_page)
    print("Page appended and dashboard updated.")
else:
    print("Page already exists.")
