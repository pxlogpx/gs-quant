"""
Copyright 2020 Goldman Sachs.
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
"""
from typing import Optional

import pandas as pd

from gs_quant.api.gs.data import QueryType
from gs_quant.entities.entity import EntityType
from gs_quant.errors import MqValueError
from gs_quant.markets.factor import Factor
from gs_quant.markets.report import RiskReport
from gs_quant.target.reports import ReportType
from gs_quant.timeseries import plot_measure_entity
from gs_quant.timeseries.measures import _extract_series_from_df

QUERY_TO_FIELD_MAP = {
    QueryType.FACTOR_EXPOSURE: 'exposure',
    QueryType.FACTOR_PNL: 'pnl',
    QueryType.FACTOR_PROPORTION_OF_RISK: 'proportionOfRisk'
}


@plot_measure_entity(EntityType.REPORT, [QueryType.FACTOR_EXPOSURE])
def factor_exposure(report_id: str, factor_name: str, *, source: str = None,
                    real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Factor exposure data associated with a factor in a factor risk report

    :param report_id: factor risk report id
    :param factor_name: factor name
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: Timeseries of factor exposure for requested factor
    """
    return _get_factor_data(report_id, factor_name, QueryType.FACTOR_EXPOSURE)


@plot_measure_entity(EntityType.REPORT, [QueryType.FACTOR_PNL])
def factor_pnl(report_id: str, factor_name: str, *, source: str = None,
               real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Factor PnL data associated with a factor in a factor risk report

    :param report_id: factor risk report id
    :param factor_name: factor name
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: Timeseries of factor pnl for requested factor
    """
    return _get_factor_data(report_id, factor_name, QueryType.FACTOR_PNL)


@plot_measure_entity(EntityType.REPORT, [QueryType.FACTOR_PROPORTION_OF_RISK])
def factor_proportion_of_risk(report_id: str, factor_name: str, *, source: str = None,
                              real_time: bool = False, request_id: Optional[str] = None) -> pd.Series:
    """
    Factor proportion of risk data associated with a factor in a factor risk report

    :param report_id: factor risk report id
    :param factor_name: factor name
    :param source: name of function caller
    :param real_time: whether to retrieve intraday data instead of EOD
    :param request_id: server request id
    :return: Timeseries of factor proportion of risk for requested factor
    """
    return _get_factor_data(report_id, factor_name, QueryType.FACTOR_PROPORTION_OF_RISK)


def _get_factor_data(report_id: str, factor_name: str, query_type: QueryType) -> pd.Series:
    # Check params
    report = RiskReport(report_id)
    if report.get_type() not in [ReportType.Portfolio_Factor_Risk, ReportType.Asset_Factor_Risk]:
        raise MqValueError('This report is not a factor risk report')
    risk_model_id = report.get_risk_model_id()
    factor = Factor(risk_model_id, factor_name)
    if factor.factor is None:
        raise MqValueError('Factor name requested is not available in the risk model associated with this report')

    # Extract relevant data for each date
    col_name = query_type.value.replace(' ', '')
    col_name = col_name[0].lower() + col_name[1:]
    data_type = QUERY_TO_FIELD_MAP[query_type]

    factor_data = report.get_factor_data(factor=factor.get_name())
    factor_exposures = [{'date': data['date'], col_name: data[data_type]} for data in factor_data
                        if data.get(data_type)]

    # Create and return timeseries
    df = pd.DataFrame(factor_exposures)
    df.set_index('date', inplace=True)
    df.index = pd.to_datetime(df.index)
    return _extract_series_from_df(df, query_type)
