// SYNTAX TEST "SQL Ex.sublime-syntax"

--simple comment
--!_! bang! comment 1
--!!! bang! comment 2
--??? bang! comment 3
--!?! bang! comment 4
--TODO bang! comment 5

-- simple comment with space
-- !_! bang! comment 1
-- !!! bang! comment 2
-- ??? bang! comment 3
-- !?! bang! comment 4
-- TODO bang! comment 5

------------------------------------------------------------
-- Oracle PL/SQL Syntax
------------------------------------------------------------

create or replace procedure PLSQL_ololo_procedure
create or replace function PLSQL_ololo_function

v_variable
c_constant
p_procedure_argument

rownum
------------------------------
select alias.row_name%found
select alias.row_name%isopen
select alias.row_name%notfound
select alias.row_name%rowcount
select alias.row_name%rowtype
select alias.row_name%type
------------------------------------------------------------

begin
	------------------------------
	if not security_pkg.is_allowed(p_method => 'check', p_user_name => 'v.pupkin') then
		return;
	end if;
	------------------------------
	loop
		...
	end loop;
	------------------------------
	end any_other_label;
	------------------------------
	select tt.id into v_id from users tt
	------------------------------
	select tt.column_value
	bulk collect into v_ids
	from table(@p_users) tt
	------------------------------
	select tt.id,
	bulk collect into v_ids
	from (
		select distinct id
		from user_history zz
		where zz.is_system != 1
	) tt
	------------------------------
	select tt.id
	bulk collect into v_id
	from users tt
	where upper(tt.system) = upper(p_system);
	------------------------------
	if (p_in_arg is null) dbms_output.putline('OMG!');
	c_constant := 42;
	l_local := 'time to debug';
	------------------------------
	v_sql_format := Q'[
		select z.*
		from :p_table_name z
		where z.:p_column_name = 1
	]';
	------------------------------
	v_sql_format := replace(v_sql_format, ':p_table_name', 'USERS');
	v_sql_format := replace(v_sql_format, ':p_column_name', 'HAS_MONEY');
	------------------------------
	open cr_result for
	select * from dual;
	------------------------------
	execute immediate v_sql_format;
	------------------------------
exception
	when no_data_found then v_id := null;
	when others then raise;
end;

------------------------------------------------------------
-- SQL Server T-SQL Syntax
------------------------------------------------------------
create procedure MSSQL_procedure
create function MSSQL_procedure
------------------------------
create procedure dbo.MSSQL_procedure
create function dbo.MSSQL_procedure
------------------------------
create procedure instance.schema.procedure
		@p_param1 bigint
	,	@p_param2 dbo.t_user_table readonly
	,	@p_param3 nvarchar(max) output
	,	@p_debug_dsql int = null
------------------------------
declare
		@v_param1 bigint
	,	@v_param2 datetime2(2)
	,	@v_param3 dbo.user_type
	,	@v_param4 int
	,	@v_param5 nvarchar(max)
------------------------------
@v_variable
@c_constant
@p_procedure_argument

@@rowcount
@@trancount
@@fetch_status

set transaction isolation level read uncommitted
set nocount off

begin
begin tran
begin transaction

save tran
save transaction
save transaction transaction_label

commit
commit tran
commit transaction

rollback
rollback tran
rollback transaction
rollback transaction transaction_label

------------------------------
select z.*
from dbo.[:p_table_name] z
where z.[:p_column_name] = 1
;
set @sql_format := N' -- dsql
	select z.*
	from dbo.[:p_table_name] z
	where z.[:p_column_name] = 1
' -- sql
;
set @sql_format := N' /* sql */
	select z.*
	from dbo.[:p_table_name] z
	where z.[:p_column_name] = 1
'; -- sql
------------------------------
bad_mssql_parameter_name@sql_format
------------------------------
-- Однострочные строки
set @var = N'Таблица описаний консультаций';
set @var = N`Таблица описаний консультаций`;
set @var = N"Таблица описаний консультаций";
------------------------------
-- Многострочные строки
set @var = N'Таблица описаний консультаций
Вторая строка'
;
set @var = N"Таблица описаний консультаций
Вторая строка"
;
------------------------------
exec  install__set_table_comment 'conferencies', N'Таблица
описаний консультаций.
Azaza!
';

exec  install__set_table_comment 'conferencies', N'Таблица описаний консультаций';
exec install__set_column_comment 'conferencies', N'accepted_offer_id', N'Принятая при создании консультации оферта';
exec install__set_column_comment 'conferencies', N'anamnesis', N'Анамнез';


set @sql_format := replace(@sql_format, N':p_table_name', N'USERS');
set @sql_format := replace(@sql_format, N':p_column_name', N'HAS_MONEY');

exec  install__set_table_comment 'conferencies', N'Таблица описаний консультаций';
exec install__set_column_comment 'conferencies', N'accepted_offer_id', N'Принятая при создании консультации оферта';
exec install__set_column_comment 'conferencies', N'anamnesis', N'Анамнез';

------------------------------
exec sp_executesql @sql_format;
exec sp_unknown @sql_format;
------------------------------
exec dbo.p_rocedure @param1,@param2,@param3;
exec p_rocedure @param1,@param2,@param3; --!?! proc_name
exec dbo.procedure @param1,@param2,@param3; --!?! proc_name
select * from dbo.func(@param1, default)
------------------------------
set @v = a_a1a.[b_b1b].a_a1a.[b_b1b].a_a1a.[b_b1b].a_a1a(@var_var)
set @v = a_a1a.[b_b1b].a_a1a.[b_b1b].a_a1a.[b_b1b](@var_var)
set @v = a_a1a.[b_b1b].a_a1a.[b_b1b].a_a1a(@var_var)
set @v = a_a1a.[b_b1b].a_a1a.[b_b1b](@var_var)
set @v = a_a1a.[b_b1b].a_a1a(@var_var)
set @v = a_a1a.[b_b1b](@var_var)
set @v = a_a1a(@var_var)
------------------------------
select a_a1a.[b_b1b].a_a1a.[b_b1b].a_a1a.[b_b1b].a_a1a
select a_a1a.[b_b1b].a_a1a.[b_b1b].a_a1a.[b_b1b]
select a_a1a.[b_b1b].a_a1a.[b_b1b].a_a1a
select a_a1a.[b_b1b].a_a1a.[b_b1b]
select a_a1a.[b_b1b].a_a1a
select a_a1a.[b_b1b]
select a_a1a
------------------------------
select * from a_a1a.[b_b1b].a_a1a.[b_b1b].a_a1a.[b_b1b].a_a1a(@var_var)
select * from a_a1a.[b_b1b].a_a1a.[b_b1b].a_a1a.[b_b1b](@var_var)
select * from a_a1a.[b_b1b].a_a1a.[b_b1b].a_a1a(@var_var)
select * from a_a1a.[b_b1b].a_a1a.[b_b1b](@var_var)
select * from a_a1a.[b_b1b].a_a1a(@var_var)
select * from a_a1a.[b_b1b](@var_var)
select * from a_a1a(@var_var)
------------------------------
insert into #att_val(att_id, object_type_id, object_id, val)
values
(
		attributes.get_att_id_for_code(@c_attcode_COMMUTATION_DATE)
	,	@c_objtype_CAMPAIGN_MEMBER
	,	@v_campaign_member_id
	,	@v_commutation_date
)
------------------------------
if(@error_code = 1) begin ... end; --!?! if is not user function
if (@error_code = 1) begin ... end;
------------------------------
create table #temp_table(id int, name varchar(100))
------------------------------
select alias.column
from #temp_table alias
------------------------------
select column_name from permanent_table;

select column_name
from permanent_table;

select column_name from permanent_table as z

select column_name
from dbo.permanent_table alias

select column_name
from dbo.permanent_table as alias
------------------------------
select alias.column_name
from permanent_table alias
------------------------------
select alias.column_name
from instance.schema.permanent_table alias

select [alias].[column_name]
from [instance].[schema].[permanent_table] as [alias]

select [alias].[column_name]
from [extra_bull_shit].[instance].[schema].[permanent_table] as [alias]

------------------------------
begin try
end try
begin catch
end catch
------------------------------
IF NOT EXISTS( select so.* from sys.objects
